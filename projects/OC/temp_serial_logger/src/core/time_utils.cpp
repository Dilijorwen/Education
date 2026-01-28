#include "time_utils.h"

#include <chrono>
#include <ctime>
#include <iomanip>
#include <sstream>

namespace timeu {

    static std::tm gmtime_safe(std::time_t t) {
        std::tm out{};
#if defined(_WIN32)
        gmtime_s(&out, &t);
#else
        gmtime_r(&t, &out);
#endif
        return out;
    }

    static std::time_t timegm_safe(std::tm* tm_utc) {
#if defined(_WIN32)
        return _mkgmtime(tm_utc);
#else
        return timegm(tm_utc);
#endif
    }

    int64_t now_epoch_ms() {
        using namespace std::chrono;
        return duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();
    }

    int64_t floor_to_hour_utc_ms(int64_t epoch_ms) {
        constexpr int64_t H = 3600'000LL;
        return (epoch_ms / H) * H;
    }

    int64_t floor_to_day_utc_ms(int64_t epoch_ms) {
        constexpr int64_t D = 86'400'000LL;
        return (epoch_ms / D) * D;
    }

    int64_t start_of_year_utc_ms(int64_t epoch_ms) {
        std::time_t sec = static_cast<std::time_t>(epoch_ms / 1000);
        std::tm tm = gmtime_safe(sec);
        std::tm y0{};
        y0.tm_year = tm.tm_year;
        y0.tm_mon  = 0;
        y0.tm_mday = 1;
        y0.tm_hour = 0;
        y0.tm_min  = 0;
        y0.tm_sec  = 0;
        std::time_t y0sec = timegm_safe(&y0);
        return static_cast<int64_t>(y0sec) * 1000;
    }

    std::string to_string_utc(int64_t epoch_ms) {
        std::time_t sec = static_cast<std::time_t>(epoch_ms / 1000);
        std::tm tm = gmtime_safe(sec);
        std::ostringstream oss;
        oss << std::put_time(&tm, "%Y-%m-%dT%H:%M:%SZ");
        return oss.str();
    }

} // namespace timeu

