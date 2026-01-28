// src/logger_main.cpp

#include "serial/serial_port.h"
#include "core/csv_log.h"
#include "core/time_utils.h"
#include "core/rolling_agg.h"
#include "core/exe_path.h"

#include <algorithm>
#include <cctype>
#include <chrono>
#include <cstdlib>
#include <filesystem>
#include <iostream>
#include <sstream>
#include <string>

static std::string trim(std::string s) {
    auto is_ws = [](unsigned char c) { return std::isspace(c) != 0; };
    while (!s.empty() && is_ws((unsigned char)s.front())) s.erase(s.begin());
    while (!s.empty() && is_ws((unsigned char)s.back())) s.pop_back();
    return s;
}

static bool parse_temp_c(const std::string& in, double& out) {
    std::string s = trim(in);
    if (s.empty()) return false;

    auto pos_eq = s.find_last_of('=');
    if (pos_eq != std::string::npos && pos_eq + 1 < s.size()) {
        s = trim(s.substr(pos_eq + 1));
    }

    std::replace(s.begin(), s.end(), ',', '.');

    char* end = nullptr;
    const double v = std::strtod(s.c_str(), &end);
    if (end == s.c_str()) return false;
    out = v;
    return true;
}

static std::string arg_value(int argc, char** argv, const std::string& key, const std::string& def) {
    for (int i = 1; i + 1 < argc; ++i) {
        if (argv[i] == key) return argv[i + 1];
    }
    return def;
}

static bool has_flag(int argc, char** argv, const std::string& key) {
    for (int i = 1; i < argc; ++i) {
        if (argv[i] == key) return true;
    }
    return false;
}

static bool has_key(int argc, char** argv, const std::string& key) {
    for (int i = 1; i < argc; ++i) {
        if (argv[i] == key) return true;
    }
    return false;
}

int main(int argc, char** argv) {
    const bool use_stdin = has_flag(argc, argv, std::string("--stdin"));
    const std::string port = arg_value(argc, argv, std::string("--port"), std::string(""));
    const int baud = std::stoi(arg_value(argc, argv, std::string("--baud"), std::string("115200")));

    std::string log_dir;
    if (has_key(argc, argv, std::string("--log-dir"))) {
        log_dir = arg_value(argc, argv, std::string("--log-dir"), std::string("logs"));
    } else {
        log_dir = (exe_path::executable_dir() / "logs").string();
    }

    std::cerr << "[MARK] log_dir=" << log_dir << "\n";
    std::cerr.flush();

    const std::string raw_path    = (std::filesystem::path(log_dir) / "raw_24h.csv").string();
    const std::string hourly_path = (std::filesystem::path(log_dir) / "hourly_30d.csv").string();
    const std::string daily_path  = (std::filesystem::path(log_dir) / "daily_ytd.csv").string();

    const std::string raw_header    = "epoch_ms,temp_c";
    const std::string hourly_header = "hour_start_epoch_ms,avg_temp_c,count";
    const std::string daily_header  = "day_start_epoch_ms,avg_temp_c,count";

    csvlog::ensure_with_header(raw_path, raw_header);
    csvlog::ensure_with_header(hourly_path, hourly_header);
    csvlog::ensure_with_header(daily_path, daily_header);

    SerialPort sp;
    if (!use_stdin) {
        if (port.empty()) return 2;
        if (!sp.open(port, baud)) return 3;
    }

    RollingAgg hour_agg;
    RollingAgg day_agg;

    int64_t now = timeu::now_epoch_ms();
    hour_agg.reset(timeu::floor_to_hour_utc_ms(now));
    day_agg.reset(timeu::floor_to_day_utc_ms(now));

    int64_t last_raw_prune_ms = now;

    auto prune_raw_24h = [&](int64_t now_ms) {
        constexpr int64_t W = 86'400'000LL;
        const int64_t cutoff = now_ms - W;
        csvlog::prune_keep_lines(raw_path, raw_header, [&](const std::string& line) {
            auto comma = line.find(',');
            if (comma == std::string::npos) return false;
            const std::string ts = line.substr(0, comma);
            char* end = nullptr;
            long long t = std::strtoll(ts.c_str(), &end, 10);
            if (end == ts.c_str()) return false;
            return (int64_t)t >= cutoff;
        });
    };

    auto prune_hourly_30d = [&](int64_t now_ms) {
        constexpr int64_t W = 30LL * 86'400'000LL;
        const int64_t cutoff = now_ms - W;
        csvlog::prune_keep_lines(hourly_path, hourly_header, [&](const std::string& line) {
            auto comma = line.find(',');
            if (comma == std::string::npos) return false;
            const std::string ts = line.substr(0, comma);
            char* end = nullptr;
            long long t = std::strtoll(ts.c_str(), &end, 10);
            if (end == ts.c_str()) return false;
            return (int64_t)t >= cutoff;
        });
    };

    auto prune_daily_ytd = [&](int64_t now_ms) {
        const int64_t cutoff = timeu::start_of_year_utc_ms(now_ms);
        csvlog::prune_keep_lines(daily_path, daily_header, [&](const std::string& line) {
            auto comma = line.find(',');
            if (comma == std::string::npos) return false;
            const std::string ts = line.substr(0, comma);
            char* end = nullptr;
            long long t = std::strtoll(ts.c_str(), &end, 10);
            if (end == ts.c_str()) return false;
            return (int64_t)t >= cutoff;
        });
    };

    auto flush_hour_bucket = [&](int64_t bucket_start_ms) {
        if (hour_agg.count <= 0) return;
        std::ostringstream oss;
        oss << bucket_start_ms << "," << hour_agg.avg() << "," << hour_agg.count;
        csvlog::append_line(hourly_path, oss.str());
    };

    auto flush_day_bucket = [&](int64_t bucket_start_ms) {
        if (day_agg.count <= 0) return;
        std::ostringstream oss;
        oss << bucket_start_ms << "," << day_agg.avg() << "," << day_agg.count;
        csvlog::append_line(daily_path, oss.str());
    };

    while (true) {
        std::string line;
        bool got = false;

        if (use_stdin) {
            if (!std::getline(std::cin, line)) break;
            got = true;
        } else {
            got = sp.read_line(line, std::chrono::milliseconds(1000));
            if (!got) continue;
        }

        double temp = 0.0;
        if (!parse_temp_c(line, temp)) continue;

        const int64_t t_ms = timeu::now_epoch_ms();

        // raw
        {
            std::ostringstream oss;
            oss << t_ms << "," << temp;
            csvlog::append_line(raw_path, oss.str());
        }

        // hourly/day aggregation
        const int64_t hour_bucket = timeu::floor_to_hour_utc_ms(t_ms);
        const int64_t day_bucket  = timeu::floor_to_day_utc_ms(t_ms);

        if (hour_bucket != hour_agg.bucket_start_ms) {
            flush_hour_bucket(hour_agg.bucket_start_ms);
            prune_hourly_30d(t_ms);
            hour_agg.reset(hour_bucket);
        }
        if (day_bucket != day_agg.bucket_start_ms) {
            flush_day_bucket(day_agg.bucket_start_ms);
            prune_daily_ytd(t_ms);
            day_agg.reset(day_bucket);
        }

        hour_agg.add(temp);
        day_agg.add(temp);

        // raw pruning раз в минуту
        if (t_ms - last_raw_prune_ms >= 60'000) {
            prune_raw_24h(t_ms);
            last_raw_prune_ms = t_ms;
        }
    }

    // финальная фиксация (при корректном завершении)
    const int64_t end_ms = timeu::now_epoch_ms();
    flush_hour_bucket(hour_agg.bucket_start_ms);
    flush_day_bucket(day_agg.bucket_start_ms);
    prune_raw_24h(end_ms);
    prune_hourly_30d(end_ms);
    prune_daily_ytd(end_ms);

    return 0;
}
