#include "sqlite_db.h"
#include <stdexcept>

SqliteDb::~SqliteDb() {
    if (db_) sqlite3_close(db_);
}

void SqliteDb::open(const std::string& path) {
    if (db_) sqlite3_close(db_);
    db_ = nullptr;

    if (sqlite3_open(path.c_str(), &db_) != SQLITE_OK) {
        std::string err = db_ ? sqlite3_errmsg(db_) : "sqlite3_open failed";
        if (db_) sqlite3_close(db_);
        db_ = nullptr;
        throw std::runtime_error(err);
    }
}

void SqliteDb::exec(const std::string& sql) {
    char* err = nullptr;
    if (sqlite3_exec(db_, sql.c_str(), nullptr, nullptr, &err) != SQLITE_OK) {
        std::string msg = err ? err : "sqlite exec failed";
        sqlite3_free(err);
        throw std::runtime_error(msg);
    }
}
