#pragma once
#include <cstdint>
#include <functional>
#include <mutex>
#include <string>

class Repo;

struct HttpConfig {
    std::string bind_host = "0.0.0.0";
    int port = 8080;
    std::string web_dir; // статика
};

class HttpServer {
public:
    HttpServer(Repo& repo, std::mutex& db_mx, const HttpConfig& cfg);

    // блокирующий старт (вызывай в отдельном потоке)
    void run();

private:
    Repo& repo_;
    std::mutex& db_mx_;
    HttpConfig cfg_;
};
