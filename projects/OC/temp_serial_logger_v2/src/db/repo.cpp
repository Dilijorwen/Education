#include "repo.h"
#include "sqlite_db.h"
#include "core/time_utils.h"

#include <sqlite3.h>
#include <stdexcept>

static void step_ok(int rc, sqlite3* db) {
    if (rc != SQLITE_DONE && rc != SQLITE_ROW) {
        throw std::runtime_error(sqlite3_errmsg(db));
    }
}

Repo::Repo(SqliteDb& db) : db_(db) {}

void Repo::insert_raw(int64_t ts_ms, double temp_c) {
    const char* sql = "INSERT OR REPLACE INTO measurements_raw(ts_ms,temp_c) VALUES(?,?);";
    sqlite3_stmt* st = nullptr;
    if (sqlite3_prepare_v2(db_.handle(), sql, -1, &st, nullptr) != SQLITE_OK) {
        throw std::runtime_error(sqlite3_errmsg(db_.handle()));
    }
    sqlite3_bind_int64(st, 1, ts_ms);
    sqlite3_bind_double(st, 2, temp_c);
    step_ok(sqlite3_step(st), db_.handle());
    sqlite3_finalize(st);
}

void Repo::upsert_hour(int64_t hour_start_ms, double avg_temp_c, int64_t count) {
    const char* sql =
        "INSERT INTO hourly_avg(hour_start_ms,avg_temp_c,count) VALUES(?,?,?) "
        "ON CONFLICT(hour_start_ms) DO UPDATE SET avg_temp_c=excluded.avg_temp_c, count=excluded.count;";
    sqlite3_stmt* st = nullptr;
    if (sqlite3_prepare_v2(db_.handle(), sql, -1, &st, nullptr) != SQLITE_OK) {
        throw std::runtime_error(sqlite3_errmsg(db_.handle()));
    }
    sqlite3_bind_int64(st, 1, hour_start_ms);
    sqlite3_bind_double(st, 2, avg_temp_c);
    sqlite3_bind_int64(st, 3, count);
    step_ok(sqlite3_step(st), db_.handle());
    sqlite3_finalize(st);
}

void Repo::upsert_day(int64_t day_start_ms, double avg_temp_c, int64_t count) {
    const char* sql =
        "INSERT INTO daily_avg(day_start_ms,avg_temp_c,count) VALUES(?,?,?) "
        "ON CONFLICT(day_start_ms) DO UPDATE SET avg_temp_c=excluded.avg_temp_c, count=excluded.count;";
    sqlite3_stmt* st = nullptr;
    if (sqlite3_prepare_v2(db_.handle(), sql, -1, &st, nullptr) != SQLITE_OK) {
        throw std::runtime_error(sqlite3_errmsg(db_.handle()));
    }
    sqlite3_bind_int64(st, 1, day_start_ms);
    sqlite3_bind_double(st, 2, avg_temp_c);
    sqlite3_bind_int64(st, 3, count);
    step_ok(sqlite3_step(st), db_.handle());
    sqlite3_finalize(st);
}

std::optional<Current> Repo::get_current() {
    const char* sql = "SELECT ts_ms,temp_c FROM measurements_raw ORDER BY ts_ms DESC LIMIT 1;";
    sqlite3_stmt* st = nullptr;
    if (sqlite3_prepare_v2(db_.handle(), sql, -1, &st, nullptr) != SQLITE_OK) {
        throw std::runtime_error(sqlite3_errmsg(db_.handle()));
    }
    int rc = sqlite3_step(st);
    if (rc == SQLITE_ROW) {
        Current c{};
        c.ts_ms = sqlite3_column_int64(st, 0);
        c.temp_c = sqlite3_column_double(st, 1);
        sqlite3_finalize(st);
        return c;
    }
    sqlite3_finalize(st);
    return std::nullopt;
}

static std::optional<Stats> stats_generic(SqliteDb& db, const char* sql, int64_t from_ms, int64_t to_ms) {
    sqlite3_stmt* st = nullptr;
    if (sqlite3_prepare_v2(db.handle(), sql, -1, &st, nullptr) != SQLITE_OK) {
        throw std::runtime_error(sqlite3_errmsg(db.handle()));
    }
    sqlite3_bind_int64(st, 1, from_ms);
    sqlite3_bind_int64(st, 2, to_ms);

    int rc = sqlite3_step(st);
    if (rc == SQLITE_ROW) {
        Stats s{};
        s.from_ms = from_ms;
        s.to_ms = to_ms;
        s.count = sqlite3_column_int64(st, 0);
        s.min_v = sqlite3_column_double(st, 1);
        s.max_v = sqlite3_column_double(st, 2);
        s.avg_v = sqlite3_column_double(st, 3);
        sqlite3_finalize(st);
        if (s.count <= 0) return std::nullopt;
        return s;
    }
    sqlite3_finalize(st);
    return std::nullopt;
}

std::optional<Stats> Repo::stats_raw(int64_t from_ms, int64_t to_ms) {
    const char* sql = "SELECT COUNT(*), MIN(temp_c), MAX(temp_c), AVG(temp_c) "
                      "FROM measurements_raw WHERE ts_ms>=? AND ts_ms<=?;";
    return stats_generic(db_, sql, from_ms, to_ms);
}

std::optional<Stats> Repo::stats_hour(int64_t from_ms, int64_t to_ms) {
    const char* sql = "SELECT SUM(count), MIN(avg_temp_c), MAX(avg_temp_c), AVG(avg_temp_c) "
                      "FROM hourly_avg WHERE hour_start_ms>=? AND hour_start_ms<=?;";
    return stats_generic(db_, sql, from_ms, to_ms);
}

std::optional<Stats> Repo::stats_day(int64_t from_ms, int64_t to_ms) {
    const char* sql = "SELECT SUM(count), MIN(avg_temp_c), MAX(avg_temp_c), AVG(avg_temp_c) "
                      "FROM daily_avg WHERE day_start_ms>=? AND day_start_ms<=?;";
    return stats_generic(db_, sql, from_ms, to_ms);
}

std::vector<Point> Repo::series_raw(int64_t from_ms, int64_t to_ms, int limit) {
    std::vector<Point> out;
    const char* sql = "SELECT ts_ms,temp_c FROM measurements_raw "
                      "WHERE ts_ms>=? AND ts_ms<=? ORDER BY ts_ms ASC LIMIT ?;";
    sqlite3_stmt* st = nullptr;
    if (sqlite3_prepare_v2(db_.handle(), sql, -1, &st, nullptr) != SQLITE_OK) {
        throw std::runtime_error(sqlite3_errmsg(db_.handle()));
    }
    sqlite3_bind_int64(st, 1, from_ms);
    sqlite3_bind_int64(st, 2, to_ms);
    sqlite3_bind_int(st, 3, limit);

    while (sqlite3_step(st) == SQLITE_ROW) {
        Point p{};
        p.t_ms = sqlite3_column_int64(st, 0);
        p.v = sqlite3_column_double(st, 1);
        p.n = 1;
        out.push_back(p);
    }
    sqlite3_finalize(st);
    return out;
}

std::vector<Point> Repo::series_hour(int64_t from_ms, int64_t to_ms) {
    std::vector<Point> out;
    const char* sql = "SELECT hour_start_ms,avg_temp_c,count FROM hourly_avg "
                      "WHERE hour_start_ms>=? AND hour_start_ms<=? ORDER BY hour_start_ms ASC;";
    sqlite3_stmt* st = nullptr;
    if (sqlite3_prepare_v2(db_.handle(), sql, -1, &st, nullptr) != SQLITE_OK) {
        throw std::runtime_error(sqlite3_errmsg(db_.handle()));
    }
    sqlite3_bind_int64(st, 1, from_ms);
    sqlite3_bind_int64(st, 2, to_ms);

    while (sqlite3_step(st) == SQLITE_ROW) {
        Point p{};
        p.t_ms = sqlite3_column_int64(st, 0);
        p.v = sqlite3_column_double(st, 1);
        p.n = sqlite3_column_int64(st, 2);
        out.push_back(p);
    }
    sqlite3_finalize(st);
    return out;
}

std::vector<Point> Repo::series_day(int64_t from_ms, int64_t to_ms) {
    std::vector<Point> out;
    const char* sql = "SELECT day_start_ms,avg_temp_c,count FROM daily_avg "
                      "WHERE day_start_ms>=? AND day_start_ms<=? ORDER BY day_start_ms ASC;";
    sqlite3_stmt* st = nullptr;
    if (sqlite3_prepare_v2(db_.handle(), sql, -1, &st, nullptr) != SQLITE_OK) {
        throw std::runtime_error(sqlite3_errmsg(db_.handle()));
    }
    sqlite3_bind_int64(st, 1, from_ms);
    sqlite3_bind_int64(st, 2, to_ms);

    while (sqlite3_step(st) == SQLITE_ROW) {
        Point p{};
        p.t_ms = sqlite3_column_int64(st, 0);
        p.v = sqlite3_column_double(st, 1);
        p.n = sqlite3_column_int64(st, 2);
        out.push_back(p);
    }
    sqlite3_finalize(st);
    return out;
}

void Repo::retention_raw_24h(int64_t now_ms) {
    const int64_t cutoff = now_ms - 86'400'000LL;
    const char* sql = "DELETE FROM measurements_raw WHERE ts_ms < ?;";
    sqlite3_stmt* st = nullptr;
    if (sqlite3_prepare_v2(db_.handle(), sql, -1, &st, nullptr) != SQLITE_OK) {
        throw std::runtime_error(sqlite3_errmsg(db_.handle()));
    }
    sqlite3_bind_int64(st, 1, cutoff);
    step_ok(sqlite3_step(st), db_.handle());
    sqlite3_finalize(st);
}

void Repo::retention_hour_30d(int64_t now_ms) {
    const int64_t cutoff = now_ms - 30LL * 86'400'000LL;
    const char* sql = "DELETE FROM hourly_avg WHERE hour_start_ms < ?;";
    sqlite3_stmt* st = nullptr;
    if (sqlite3_prepare_v2(db_.handle(), sql, -1, &st, nullptr) != SQLITE_OK) {
        throw std::runtime_error(sqlite3_errmsg(db_.handle()));
    }
    sqlite3_bind_int64(st, 1, cutoff);
    step_ok(sqlite3_step(st), db_.handle());
    sqlite3_finalize(st);
}

void Repo::retention_day_ytd(int64_t now_ms) {
    const int64_t cutoff = timeu::start_of_year_utc_ms(now_ms);
    const char* sql = "DELETE FROM daily_avg WHERE day_start_ms < ?;";
    sqlite3_stmt* st = nullptr;
    if (sqlite3_prepare_v2(db_.handle(), sql, -1, &st, nullptr) != SQLITE_OK) {
        throw std::runtime_error(sqlite3_errmsg(db_.handle()));
    }
    sqlite3_bind_int64(st, 1, cutoff);
    step_ok(sqlite3_step(st), db_.handle());
    sqlite3_finalize(st);
}
