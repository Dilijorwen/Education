#if !defined(_WIN32)

#include "serial/serial_port.h"

#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <sys/select.h>
#include <termios.h>
#include <unistd.h>

#include <string>
#include <vector>

struct SerialPort::Impl {
    int fd = -1;
    std::string buf;
};

static speed_t baud_to_speed(int baud) {
    switch (baud) {
        case 9600: return B9600;
        case 19200: return B19200;
        case 38400: return B38400;
        case 57600: return B57600;
        case 115200: return B115200;
        default: return B115200;
    }
}

SerialPort::SerialPort() : impl_(new Impl) {}
SerialPort::~SerialPort() { close(); delete impl_; }

bool SerialPort::open(const std::string& port_name, int baud) {
    close();
    impl_->fd = ::open(port_name.c_str(), O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (impl_->fd < 0) return false;

    termios tty{};
    if (tcgetattr(impl_->fd, &tty) != 0) {
        close();
        return false;
    }

    cfsetospeed(&tty, baud_to_speed(baud));
    cfsetispeed(&tty, baud_to_speed(baud));

    tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8;
    tty.c_cflag |= (CLOCAL | CREAD);
    tty.c_cflag &= ~(PARENB | PARODD);
    tty.c_cflag &= ~CSTOPB;
    tty.c_cflag &= ~CRTSCTS;

    tty.c_iflag &= ~(IXON | IXOFF | IXANY);
    tty.c_iflag &= ~(IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL);

    tty.c_lflag = 0;
    tty.c_oflag = 0;

    tty.c_cc[VMIN]  = 0;
    tty.c_cc[VTIME] = 0;

    if (tcsetattr(impl_->fd, TCSANOW, &tty) != 0) {
        close();
        return false;
    }
    impl_->buf.clear();
    return true;
}

void SerialPort::close() {
    if (impl_->fd >= 0) {
        ::close(impl_->fd);
        impl_->fd = -1;
    }
    impl_->buf.clear();
}

bool SerialPort::is_open() const {
    return impl_->fd >= 0;
}

bool SerialPort::read_line(std::string& out_line, std::chrono::milliseconds timeout) {
    out_line.clear();
    if (impl_->fd < 0) return false;

    auto try_extract = [&]() -> bool {
        auto pos = impl_->buf.find('\n');
        if (pos == std::string::npos) return false;
        out_line = impl_->buf.substr(0, pos);
        impl_->buf.erase(0, pos + 1);
        if (!out_line.empty() && out_line.back() == '\r') out_line.pop_back();
        return true;
    };

    if (try_extract()) return true;

    fd_set rfds;
    FD_ZERO(&rfds);
    FD_SET(impl_->fd, &rfds);

    timeval tv{};
    tv.tv_sec = static_cast<long>(timeout.count() / 1000);
    tv.tv_usec = static_cast<long>((timeout.count() % 1000) * 1000);

    int r = select(impl_->fd + 1, &rfds, nullptr, nullptr, &tv);
    if (r <= 0) return false;

    char tmp[256];
    ssize_t n = ::read(impl_->fd, tmp, sizeof(tmp));
    if (n <= 0) return false;
    impl_->buf.append(tmp, tmp + n);

    return try_extract();
}

#endif
