#include "schema.h"

namespace dbschema {

    std::string create_sql() {
        return R"SQL(
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS measurements_raw (
  ts_ms  INTEGER PRIMARY KEY,
  temp_c REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS hourly_avg (
  hour_start_ms INTEGER PRIMARY KEY,
  avg_temp_c    REAL NOT NULL,
  count         INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS daily_avg (
  day_start_ms  INTEGER PRIMARY KEY,
  avg_temp_c    REAL NOT NULL,
  count         INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_raw_ts ON measurements_raw(ts_ms);
)SQL";
    }

}
