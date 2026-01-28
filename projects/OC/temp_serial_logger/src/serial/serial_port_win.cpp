#if defined(_WIN32)

#include "serial/serial_port.h"

#ifndef NOMINMAX
  #define NOMINMAX
#endif
#include <windows.h>

#include <string>

struct SerialPort::Impl {
    HANDLE h = INVALID_HANDLE_VALUE;
    std::string buf;
};

static std::wstring to_w(const std::string& s) {
    if (s.empty()) return L"";
    int len = MultiByteToWideChar(CP_UTF8, 0, s.c_str(), (int)s.size(), nullptr, 0);
    std::wstring w(len, L'\0');
    MultiByteToWideChar(CP_UTF8, 0, s.c_str(), (int)s.size(), &w[0], len);
    return w;
}

SerialPort::SerialPort() : impl_(new Impl) {}
SerialPort::~SerialPort() { close(); delete impl_; }

bool SerialPort::open(const std::string& port_name, int baud) {
    close();

    // COM10+ требует префикс \\.\COM10
    std::string pn = port_name;
    if (pn.rfind("COM", 0) == 0 && pn.size() > 4) {
        pn = "\\\\.\\" + pn;
    } else if (pn.rfind("\\\\.", 0) != 0 && pn.rfind("\\\\", 0) != 0 && pn.rfind("COM", 0) == 0) {
        pn = "\\\\.\\" + pn;
    }

    std::wstring wpn = to_w(pn);

    impl_->h = CreateFileW(
        wpn.c_str(),
        GENERIC_READ,
        0,
        nullptr,
        OPEN_EXISTING,
        0,
        nullptr
    );
    if (impl_->h == INVALID_HANDLE_VALUE) return false;

    DCB dcb{};
    dcb.DCBlength = sizeof(DCB);
    if (!GetCommState(impl_->h, &dcb)) {
        close();
        return false;
    }

    dcb.BaudRate = (DWORD)baud;
    dcb.ByteSize = 8;
    dcb.Parity = NOPARITY;
    dcb.StopBits = ONESTOPBIT;
    dcb.fOutxCtsFlow = FALSE;
    dcb.fOutxDsrFlow = FALSE;
    dcb.fDtrControl = DTR_CONTROL_ENABLE;
    dcb.fRtsControl = RTS_CONTROL_ENABLE;

    if (!SetCommState(impl_->h, &dcb)) {
        close();
        return false;
    }

    COMMTIMEOUTS to{};
    to.ReadIntervalTimeout = 50;
    to.ReadTotalTimeoutConstant = 50;
    to.ReadTotalTimeoutMultiplier = 1;
    SetCommTimeouts(impl_->h, &to);

    impl_->buf.clear();
    return true;
}

void SerialPort::close() {
    if (impl_->h != INVALID_HANDLE_VALUE) {
        CloseHandle(impl_->h);
        impl_->h = INVALID_HANDLE_VALUE;
    }
    impl_->buf.clear();
}

bool SerialPort::is_open() const {
    return impl_->h != INVALID_HANDLE_VALUE;
}

bool SerialPort::read_line(std::string& out_line, std::chrono::milliseconds timeout) {
    out_line.clear();
    if (impl_->h == INVALID_HANDLE_VALUE) return false;

    auto try_extract = [&]() -> bool {
        auto pos = impl_->buf.find('\n');
        if (pos == std::string::npos) return false;
        out_line = impl_->buf.substr(0, pos);
        impl_->buf.erase(0, pos + 1);
        if (!out_line.empty() && out_line.back() == '\r') out_line.pop_back();
        return true;
    };

    if (try_extract()) return true;

    DWORD start = GetTickCount();
    while (true) {
        char tmp[256];
        DWORD read = 0;
        BOOL ok = ReadFile(impl_->h, tmp, (DWORD)sizeof(tmp), &read, nullptr);
        if (ok && read > 0) {
            impl_->buf.append(tmp, tmp + read);
            if (try_extract()) return true;
        }

        DWORD elapsed = GetTickCount() - start;
        if (elapsed >= (DWORD)timeout.count()) return false;
        Sleep(5);
    }
}

#endif
