#include "server.h"
#include "db/repo.h"

#include "httplib.h"
#include "json.hpp"

#include <filesystem>
#include <optional>
#include <string>

using json = nlohmann::json;

static std::optional<int64_t> q_i64(const httplib::Request& req, const char* name) {
    if (!req.has_param(name)) return std::nullopt;
    try {
        return std::stoll(req.get_param_value(name));
    } catch (...) {
        return std::nullopt;
    }
}

static std::string q_bucket(const httplib::Request& req) {
    if (!req.has_param("bucket")) return "raw";
    auto b = req.get_param_value("bucket");
    if (b == "raw" || b == "hour" || b == "day") return b;
    return "raw";
}

HttpServer::HttpServer(Repo& repo, std::mutex& db_mx, const HttpConfig& cfg)
    : repo_(repo), db_mx_(db_mx), cfg_(cfg) {}

void HttpServer::run() {
    httplib::Server svr;

    svr.Get("/api/current", [&](const httplib::Request&, httplib::Response& res) {
        std::lock_guard<std::mutex> lk(db_mx_);
        auto cur = repo_.get_current();
        if (!cur) {
            res.status = 404;
            res.set_content(R"JSON({"error":"no data"})JSON", "application/json");
            return;
        }
        json j;
        j["ts_ms"] = cur->ts_ms;
        j["temp_c"] = cur->temp_c;
        res.set_content(j.dump(), "application/json");
    });

    svr.Get("/api/stats", [&](const httplib::Request& req, httplib::Response& res) {
        auto from = q_i64(req, "from");
        auto to = q_i64(req, "to");
        if (!from || !to) {
            res.status = 400;
            res.set_content(R"JSON({"error":"need from,to (epoch ms)"})JSON", "application/json");
            return;
        }

        const auto bucket = q_bucket(req);

        std::lock_guard<std::mutex> lk(db_mx_);
        std::optional<Stats> st;
        if (bucket == "raw") st = repo_.stats_raw(*from, *to);
        else if (bucket == "hour") st = repo_.stats_hour(*from, *to);
        else st = repo_.stats_day(*from, *to);

        if (!st) {
            res.status = 404;
            res.set_content(R"JSON({"error":"no data in range"})JSON", "application/json");
            return;
        }

        json j;
        j["bucket"] = bucket;
        j["from"] = st->from_ms;
        j["to"] = st->to_ms;
        j["count"] = st->count;
        j["min"] = st->min_v;
        j["max"] = st->max_v;
        j["avg"] = st->avg_v;
        res.set_content(j.dump(), "application/json");
    });

    svr.Get("/api/series", [&](const httplib::Request& req, httplib::Response& res) {
        auto from = q_i64(req, "from");
        auto to = q_i64(req, "to");
        if (!from || !to) {
            res.status = 400;
            res.set_content(R"JSON({"error":"need from,to (epoch ms)"})JSON", "application/json");
            return;
        }

        const auto bucket = q_bucket(req);

        int limit = 5000;
        if (req.has_param("limit")) {
            try { limit = std::stoi(req.get_param_value("limit")); } catch (...) {}
            if (limit < 1) limit = 1;
            if (limit > 200000) limit = 200000;
        }

        std::lock_guard<std::mutex> lk(db_mx_);
        std::vector<Point> pts;
        if (bucket == "raw") pts = repo_.series_raw(*from, *to, limit);
        else if (bucket == "hour") pts = repo_.series_hour(*from, *to);
        else pts = repo_.series_day(*from, *to);

        json j;
        j["bucket"] = bucket;
        j["from"] = *from;
        j["to"] = *to;
        j["points"] = json::array();
        for (const auto& p : pts) {
            j["points"].push_back({{"t", p.t_ms}, {"v", p.v}, {"n", p.n}});
        }
        res.set_content(j.dump(), "application/json");
    });

    if (!cfg_.web_dir.empty() && std::filesystem::exists(cfg_.web_dir)) {
        svr.set_mount_point("/", cfg_.web_dir.c_str());
    }

    svr.listen(cfg_.bind_host.c_str(), cfg_.port);
}
