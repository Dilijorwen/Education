#include "serial/serial_port.h"

#include "core/time_utils.h"
#include "core/rolling_agg.h"
#include "core/exe_path.h"

#include "db/sqlite_db.h"
#include "db/schema.h"
#include "db/repo.h"

#include "http/server.h"

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cctype>
#include <cstdlib>
#include <filesystem>
#include <iostream>
#include <mutex>
#include <sstream>
#include <string>
#include <thread>

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
    for (int i = 1; i < argc; ++i) if (argv[i] == key) return true;
    return false;
}

static bool has_key(int argc, char** argv, const std::string& key) {
    for (int i = 1; i < argc; ++i) if (argv[i] == key) return true;
    return false;
}

int main(int argc, char** argv) {
    const bool use_stdin = has_flag(argc, argv, "--stdin");
    const std::string port = arg_value(argc, argv, "--port", "");
    const int baud = std::stoi(arg_value(argc, argv, "--baud", "115200"));

    int http_port = std::stoi(arg_value(argc, argv, "--http", "8080"));

    std::string db_path;
    if (has_key(argc, argv, "--db")) {
        db_path = arg_value(argc, argv, "--db", "temps.sqlite");
    } else {
        db_path = (exe_path::executable_dir() / "data" / "temps.sqlite").string();
    }

    std::string web_dir;
    if (has_key(argc, argv, "--web")) {
        web_dir = arg_value(argc, argv, "--web", "");
    } else {
        web_dir = (exe_path::executable_dir() / "web").string();
    }

    std::filesystem::create_directories(std::filesystem::path(db_path).parent_path());

    SqliteDb db;
    db.open(db_path);
    db.exec(dbschema::create_sql());

    Repo repo(db);
    std::mutex db_mx;

    SerialPort sp;
    if (!use_stdin) {
        if (port.empty()) {
            std::cerr << "need --port or --stdin\n";
            return 2;
        }
        if (!sp.open(port, baud)) {
            std::cerr << "cannot open port: " << port << "\n";
            return 3;
        }
    }

    // in-memory aggregators (flush to DB on bucket change)
    RollingAgg hour_agg;
    RollingAgg day_agg;

    const int64_t now = timeu::now_epoch_ms();
    hour_agg.reset(timeu::floor_to_hour_utc_ms(now));
    day_agg.reset(timeu::floor_to_day_utc_ms(now));

    std::atomic<bool> stop{false};

    // HTTP server thread
    HttpConfig cfg;
    cfg.port = http_port;
    cfg.web_dir = web_dir;

    HttpServer server(repo, db_mx, cfg);
    std::thread http_thr([&]() { server.run(); });

    // reader loop (main thread)
    int64_t last_retention_ms = now;

    auto flush_hour = [&](int64_t bucket_start_ms) {
        if (hour_agg.count <= 0) return;
        std::lock_guard<std::mutex> lk(db_mx);
        repo.upsert_hour(bucket_start_ms, hour_agg.avg(), hour_agg.count);
    };

    auto flush_day = [&](int64_t bucket_start_ms) {
        if (day_agg.count <= 0) return;
        std::lock_guard<std::mutex> lk(db_mx);
        repo.upsert_day(bucket_start_ms, day_agg.avg(), day_agg.count);
    };

    while (!stop.load()) {
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

        // insert raw
        {
            std::lock_guard<std::mutex> lk(db_mx);
            repo.insert_raw(t_ms, temp);
        }

        // bucket switches
        const int64_t hour_bucket = timeu::floor_to_hour_utc_ms(t_ms);
        const int64_t day_bucket  = timeu::floor_to_day_utc_ms(t_ms);

        if (hour_bucket != hour_agg.bucket_start_ms) {
            flush_hour(hour_agg.bucket_start_ms);
            hour_agg.reset(hour_bucket);
        }
        if (day_bucket != day_agg.bucket_start_ms) {
            flush_day(day_agg.bucket_start_ms);
            day_agg.reset(day_bucket);
        }

        hour_agg.add(temp);
        day_agg.add(temp);

        // retention once per minute
        if (t_ms - last_retention_ms >= 60'000) {
            std::lock_guard<std::mutex> lk(db_mx);
            repo.retention_raw_24h(t_ms);
            repo.retention_hour_30d(t_ms);
            repo.retention_day_ytd(t_ms);
            last_retention_ms = t_ms;
        }
    }

    // final flush
    const int64_t end_ms = timeu::now_epoch_ms();
    flush_hour(hour_agg.bucket_start_ms);
    flush_day(day_agg.bucket_start_ms);
    {
        std::lock_guard<std::mutex> lk(db_mx);
        repo.retention_raw_24h(end_ms);
        repo.retention_hour_30d(end_ms);
        repo.retention_day_ytd(end_ms);
    }

    // httplib::Server::listen() blocking; для корректного stop нужен отдельный механизм.
    // В учебной сдаче достаточно завершения по Ctrl+C и перезапуска.

    http_thr.detach();
    return 0;
}
