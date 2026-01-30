#pragma once
#include <sqlite3.h>
#include <string>

class SqliteDb {
public:
    SqliteDb() = default;
    ~SqliteDb();

    SqliteDb(const SqliteDb&) = delete;
    SqliteDb& operator=(const SqliteDb&) = delete;

    void open(const std::string& path);
    void exec(const std::string& sql);

    sqlite3* handle() const { return db_; }

private:
    sqlite3* db_ = nullptr;
};
