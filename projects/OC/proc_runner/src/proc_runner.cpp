#include "proc_runner.hpp"

#include <cstring>
#include <sstream>

#ifdef _WIN32
  #ifndef NOMINMAX
    #define NOMINMAX
  #endif
  #include <windows.h>
#else
  #include <unistd.h>
  #include <sys/types.h>
  #include <sys/wait.h>
  #include <signal.h>
  #include <errno.h>
#endif

namespace proc_runner {

static std::string quote_windows_arg(const std::string& s) {
    // Простая стратегия: если пробелов/табов/кавычек нет — без кавычек,
    // иначе оборачиваем в "..." и экранируем внутренние ".
    bool need = false;
    for (char c : s) {
        if (c == ' ' || c == '\t' || c == '"') { need = true; break; }
    }
    if (!need) return s;

    std::string out = "\"";
    for (char c : s) {
        if (c == '"') out += "\\\"";
        else out += c;
    }
    out += "\"";
    return out;
}

Process::~Process() {
#ifdef _WIN32
    if (owns_) {
        if (hThread_) CloseHandle((HANDLE)hThread_);
        if (hProcess_) CloseHandle((HANDLE)hProcess_);
    }
#endif
}

Process::Process(Process&& other) noexcept {
    *this = std::move(other);
}

Process& Process::operator=(Process&& other) noexcept {
    if (this == &other) return *this;

#ifdef _WIN32
    hProcess_ = other.hProcess_;
    hThread_  = other.hThread_;
    pid_      = other.pid_;
    owns_     = other.owns_;

    other.hProcess_ = nullptr;
    other.hThread_  = nullptr;
    other.pid_      = 0;
    other.owns_     = false;
#else
    pid_  = other.pid_;
    owns_ = other.owns_;
    other.pid_ = -1;
    other.owns_ = false;
#endif
    return *this;
}

std::uint32_t Process::pid() const {
#ifdef _WIN32
    return pid_;
#else
    return pid_ < 0 ? 0u : static_cast<std::uint32_t>(pid_);
#endif
}

bool Process::valid() const {
#ifdef _WIN32
    return hProcess_ != nullptr && pid_ != 0;
#else
    return pid_ > 0;
#endif
}

bool Process::is_running() const {
    if (!valid()) return false;

#ifdef _WIN32
    DWORD code = 0;
    if (!GetExitCodeProcess((HANDLE)hProcess_, &code)) return false;
    return code == STILL_ACTIVE;
#else
    int status = 0;
    pid_t r = waitpid(pid_, &status, WNOHANG);
    if (r == 0) return true;       // ещё работает
    if (r == pid_) return false;   // уже завершился (и мог быть "собран" этим вызовом)
    return false;
#endif
}

WaitResult Process::wait() {
    return wait_for(-1);
}

WaitResult Process::wait_for(int timeout_ms) {
    WaitResult res;

    if (!valid()) {
        res.status = WaitStatus::Failed;
        return res;
    }
#ifdef _WIN32
    DWORD wait_ms = (timeout_ms < 0) ? INFINITE : (DWORD)timeout_ms;
    DWORD w = WaitForSingleObject((HANDLE)hProcess_, wait_ms);

    if (w == WAIT_TIMEOUT) {
        res.status = WaitStatus::StillRunning;
        return res;
    }
    if (w != WAIT_OBJECT_0) {
        res.status = WaitStatus::Failed;
        return res;
    }

    DWORD code = 0;
    if (!GetExitCodeProcess((HANDLE)hProcess_, &code)) {
        res.status = WaitStatus::Failed;
        return res;
    }

    res.status = WaitStatus::Exited;
    res.exit_code = static_cast<int>(code);
    return res;
#else
    if (timeout_ms == 0) {
        int status = 0;
        pid_t r = waitpid(pid_, &status, WNOHANG);
        if (r == 0) {
            res.status = WaitStatus::StillRunning;
            return res;
        }
        if (r != pid_) {
            res.status = WaitStatus::Failed;
            return res;
        }

        if (WIFEXITED(status)) {
            res.status = WaitStatus::Exited;
            res.exit_code = WEXITSTATUS(status);
            return res;
        }
        if (WIFSIGNALED(status)) {
            res.status = WaitStatus::Exited;
            res.exit_code = 128 + WTERMSIG(status);
            return res;
        }

        res.status = WaitStatus::Failed;
        return res;
    }

    if (timeout_ms < 0) {
        int status = 0;
        pid_t r = waitpid(pid_, &status, 0);
        if (r != pid_) {
            res.status = WaitStatus::Failed;
            return res;
        }

        if (WIFEXITED(status)) {
            res.status = WaitStatus::Exited;
            res.exit_code = WEXITSTATUS(status);
            return res;
        }
        if (WIFSIGNALED(status)) {
            res.status = WaitStatus::Exited;
            res.exit_code = 128 + WTERMSIG(status);
            return res;
        }

        res.status = WaitStatus::Failed;
        return res;
    }

    // POSIX-ожидание с таймаутом: poll через waitpid(WNOHANG) + sleep
    const int step_ms = 20;
    int waited = 0;

    while (waited < timeout_ms) {
        int status = 0;
        pid_t r = waitpid(pid_, &status, WNOHANG);
        if (r == 0) {
            usleep(step_ms * 1000);
            waited += step_ms;
            continue;
        }
        if (r != pid_) {
            res.status = WaitStatus::Failed;
            return res;
        }

        if (WIFEXITED(status)) {
            res.status = WaitStatus::Exited;
            res.exit_code = WEXITSTATUS(status);
            return res;
        }
        if (WIFSIGNALED(status)) {
            res.status = WaitStatus::Exited;
            res.exit_code = 128 + WTERMSIG(status);
            return res;
        }

        res.status = WaitStatus::Failed;
        return res;
    }

    res.status = WaitStatus::StillRunning;
    return res;
#endif
}

bool Process::terminate() {
    if (!valid()) return false;

#ifdef _WIN32
    return TerminateProcess((HANDLE)hProcess_, 1) ? true : false;
#else
    return kill(pid_, SIGTERM) == 0;
#endif
}

std::optional<Process> spawn(
    const std::string& program,
    const std::vector<std::string>& args,
    const std::optional<std::string>& working_dir
) {
#ifdef _WIN32
    STARTUPINFOA si;
    PROCESS_INFORMATION pi;
    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));

    std::ostringstream cmd;
    cmd << quote_windows_arg(program);
    for (const auto& a : args) {
        cmd << " " << quote_windows_arg(a);
    }
    std::string cmdline = cmd.str();

    // CreateProcess может модифицировать буфер командной строки
    std::vector<char> buffer(cmdline.begin(), cmdline.end());
    buffer.push_back('\0');

    const char* cwd = working_dir ? working_dir->c_str() : nullptr;

    BOOL ok = CreateProcessA(
        nullptr,                // lpApplicationName
        buffer.data(),          // lpCommandLine
        nullptr,                // lpProcessAttributes
        nullptr,                // lpThreadAttributes
        FALSE,                  // bInheritHandles
        CREATE_NO_WINDOW,       // dwCreationFlags (фон без консольного окна)
        nullptr,                // lpEnvironment
        cwd,                    // lpCurrentDirectory
        &si,
        &pi
    );

    if (!ok) return std::nullopt;

    Process p;
    p.hProcess_ = (void*)pi.hProcess;
    p.hThread_  = (void*)pi.hThread;
    p.pid_      = (std::uint32_t)pi.dwProcessId;
    p.owns_     = true;
    return p;

#else
    pid_t pid = fork();
    if (pid < 0) return std::nullopt;

    if (pid == 0) {
        if (working_dir) {
            (void)chdir(working_dir->c_str());
        }

        // argv: program + args + null
        std::vector<char*> argv;
        argv.reserve(args.size() + 2);
        argv.push_back(const_cast<char*>(program.c_str()));
        for (const auto& a : args) argv.push_back(const_cast<char*>(a.c_str()));
        argv.push_back(nullptr);

        // execvp ищет program в PATH, если это не путь
        execvp(program.c_str(), argv.data());

        // Если exec не сработал — код ошибки 127
        _exit(127);
    }

    Process p;
    p.pid_ = (int)pid;
    p.owns_ = true;
    return p;
#endif
}

} // namespace proc_runner
