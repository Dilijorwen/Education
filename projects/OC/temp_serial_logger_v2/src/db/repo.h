#pragma once
#include <cstdint>
#include <optional>
#include <string>
#include <vector>

class SqliteDb;

struct Current {
    int64_t ts_ms;
    double temp_c;
};

struct Stats {
    int64_t from_ms;
    int64_t to_ms;
    int64_t count;
    double min_v;
    double max_v;
    double avg_v;
};

struct Point {
    int64_t t_ms;
    double v;
    int64_t n; // count (для raw можно 1)
};

class Repo {
public:
    explicit Repo(SqliteDb& db);

    void insert_raw(int64_t ts_ms, double temp_c);

    void upsert_hour(int64_t hour_start_ms, double avg_temp_c, int64_t count);
    void upsert_day(int64_t day_start_ms, double avg_temp_c, int64_t count);

    std::optional<Current> get_current();

    std::optional<Stats> stats_raw(int64_t from_ms, int64_t to_ms);
    std::optional<Stats> stats_hour(int64_t from_ms, int64_t to_ms);
    std::optional<Stats> stats_day(int64_t from_ms, int64_t to_ms);

    std::vector<Point> series_raw(int64_t from_ms, int64_t to_ms, int limit);
    std::vector<Point> series_hour(int64_t from_ms, int64_t to_ms);
    std::vector<Point> series_day(int64_t from_ms, int64_t to_ms);

    void retention_raw_24h(int64_t now_ms);
    void retention_hour_30d(int64_t now_ms);
    void retention_day_ytd(int64_t now_ms);

private:
    SqliteDb& db_;
};
