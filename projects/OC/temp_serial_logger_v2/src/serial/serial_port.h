#pragma once
#include <cstdint>
#include <string>
#include <chrono>

class SerialPort {
public:
    SerialPort();
    ~SerialPort();

    SerialPort(const SerialPort&) = delete;
    SerialPort& operator=(const SerialPort&) = delete;

    bool open(const std::string& port_name, int baud);
    void close();
    bool is_open() const;

    // читает строку до '\n'. true если строка получена, false если таймаут/ошибка
    bool read_line(std::string& out_line, std::chrono::milliseconds timeout);

private:
    struct Impl;
    Impl* impl_;
};
