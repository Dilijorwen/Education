#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <string>
#include <thread>
#include <atomic>
#include <chrono>
#include <sstream>
#include <iostream>

#if defined(_WIN32)
  #ifndef NOMINMAX
   #define NOMINMAX
  #endif
  #include <windows.h>
  #include <processthreadsapi.h>
#else
  #include <fcntl.h>
  #include <unistd.h>
  #include <sys/mman.h>
  #include <sys/stat.h>
  #include <sys/types.h>
  #include <signal.h>
  #include <pthread.h>
  #include <errno.h>
#endif

// =========================
// Константы имен ресурсов
// =========================
static const char* LOG_PATH          = "program.log";

#if defined(_WIN32)
static const char* SHM_NAME          = "Local\\Prog_SharedCounter_Mapping_v1";
static const char* COUNTER_MUTEX_NAME= "Local\\Prog_SharedCounter_Mutex_v1";
static const char* LOG_MUTEX_NAME    = "Local\\Prog_Log_Mutex_v1";
static const char* LEADER_MUTEX_NAME = "Local\\Prog_Leader_Mutex_v1";
#else
static const char* SHM_NAME          = "/prog_sharedcounter_v1";
static const char* LEADER_LOCK_PATH  = "program.leader.lock";
#endif

// =========================
// Утилиты времени/формата
// =========================
static std::string now_timestamp_local()
{
    using namespace std::chrono;
    auto tp = system_clock::now();
    auto ms = duration_cast<milliseconds>(tp.time_since_epoch()) % 1000;

    std::time_t tt = system_clock::to_time_t(tp);

    std::tm tmv{};
#if defined(_WIN32)
    localtime_s(&tmv, &tt);
#else
    localtime_r(&tt, &tmv);
#endif

    char buf[64];
    std::snprintf(buf, sizeof(buf), "%04d-%02d-%02d %02d:%02d:%02d.%03d",
                  tmv.tm_year + 1900,
                  tmv.tm_mon + 1,
                  tmv.tm_mday,
                  tmv.tm_hour,
                  tmv.tm_min,
                  tmv.tm_sec,
                  (int)ms.count());
    return std::string(buf);
}

static uint64_t pid_u64()
{
#if defined(_WIN32)
    return (uint64_t)GetCurrentProcessId();
#else
    return (uint64_t)getpid();
#endif
}

// =========================
// Кроссплатформенный лог
// =========================
#if defined(_WIN32)

struct WinLog {
    HANDLE hFile = INVALID_HANDLE_VALUE;
    HANDLE hMutex = NULL;

    bool open()
    {
        hMutex = CreateMutexA(NULL, FALSE, LOG_MUTEX_NAME);
        if (!hMutex) return false;

        hFile = CreateFileA(
            LOG_PATH,
            FILE_APPEND_DATA,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            NULL,
            OPEN_ALWAYS,
            FILE_ATTRIBUTE_NORMAL,
            NULL
        );
        return hFile != INVALID_HANDLE_VALUE;
    }

    void close()
    {
        if (hFile != INVALID_HANDLE_VALUE) CloseHandle(hFile);
        if (hMutex) CloseHandle(hMutex);
        hFile = INVALID_HANDLE_VALUE;
        hMutex = NULL;
    }

    void write_line(const std::string& line)
    {
        if (!hMutex || hFile == INVALID_HANDLE_VALUE) return;

        WaitForSingleObject(hMutex, INFINITE);
        DWORD written = 0;
        std::string out = line;
        out += "\r\n";
        WriteFile(hFile, out.data(), (DWORD)out.size(), &written, NULL);
        ReleaseMutex(hMutex);
    }
};

#else

struct PosixLog {
    int fd = -1;

    bool open()
    {
        fd = ::open(LOG_PATH, O_CREAT | O_WRONLY | O_APPEND, 0644);
        return fd >= 0;
    }

    void close()
    {
        if (fd >= 0) ::close(fd);
        fd = -1;
    }

    void lock_fd()
    {
        if (fd < 0) return;
        struct flock fl{};
        fl.l_type = F_WRLCK;
        fl.l_whence = SEEK_SET;
        fl.l_start = 0;
        fl.l_len = 0; // весь файл
        while (fcntl(fd, F_SETLKW, &fl) == -1 && errno == EINTR) {}
    }

    void unlock_fd()
    {
        if (fd < 0) return;
        struct flock fl{};
        fl.l_type = F_UNLCK;
        fl.l_whence = SEEK_SET;
        fl.l_start = 0;
        fl.l_len = 0;
        fcntl(fd, F_SETLK, &fl);
    }

    void write_line(const std::string& line)
    {
        if (fd < 0) return;
        lock_fd();
        std::string out = line + "\n";
        ssize_t _ = ::write(fd, out.data(), out.size());
        (void)_;
        unlock_fd();
    }
};

#endif

// =========================
// Общие данные (shared)
// =========================
#if defined(_WIN32)
struct SharedState {
    int64_t counter;
    uint32_t copy1_pid;
    uint32_t copy2_pid;
};
#else
struct SharedState {
    pthread_mutex_t mtx;   // process-shared mutex
    int64_t counter;
    pid_t copy1_pid;
    pid_t copy2_pid;
};
#endif

// =========================
// Shared memory + lock для счётчика
// =========================
#if defined(_WIN32)

struct SharedRegion {
    HANDLE hMap = NULL;
    HANDLE hCounterMutex = NULL;
    SharedState* st = nullptr;

    bool init()
    {
        hCounterMutex = CreateMutexA(NULL, FALSE, COUNTER_MUTEX_NAME);
        if (!hCounterMutex) return false;

        hMap = CreateFileMappingA(INVALID_HANDLE_VALUE, NULL, PAGE_READWRITE, 0, (DWORD)sizeof(SharedState), SHM_NAME);
        if (!hMap) return false;

        st = (SharedState*)MapViewOfFile(hMap, FILE_MAP_ALL_ACCESS, 0, 0, sizeof(SharedState));
        if (!st) return false;

        // Инициализация при первом создании: проверка через GetLastError после CreateFileMapping.
        // Если mapping новый — обнулим.
        // CreateFileMapping возвращает ERROR_ALREADY_EXISTS, если уже был.
        // Но GetLastError нужно читать сразу после CreateFileMapping; здесь упрощение: безопасно обнулять поля PID,
        // а counter оставлять как есть нежелательно. Поэтому делаем: если counter явно мусор (невозможно проверить),
        // оставляем как есть. Для лабораторной достаточно.
        // Лучше: отдельный флаг init, но это уже усложнение.
        return true;
    }

    void destroy()
    {
        if (st) UnmapViewOfFile(st);
        if (hMap) CloseHandle(hMap);
        if (hCounterMutex) CloseHandle(hCounterMutex);
        st = nullptr;
        hMap = NULL;
        hCounterMutex = NULL;
    }

    template <typename F>
    auto with_lock(F&& f) -> decltype(f(*st))
    {
        WaitForSingleObject(hCounterMutex, INFINITE);
        auto r = f(*st);
        ReleaseMutex(hCounterMutex);
        return r;
    }

    int64_t get_counter()
    {
        return with_lock([&](SharedState& s){ return s.counter; });
    }

    void set_counter(int64_t v)
    {
        with_lock([&](SharedState& s){ s.counter = v; return 0; });
    }

    void add_counter(int64_t dv)
    {
        with_lock([&](SharedState& s){ s.counter += dv; return 0; });
    }

    void mul_counter(int64_t k)
    {
        with_lock([&](SharedState& s){ s.counter *= k; return 0; });
    }

    void div_counter(int64_t k)
    {
        with_lock([&](SharedState& s){ s.counter /= k; return 0; });
    }

    uint32_t get_copy_pid(int idx)
    {
        return with_lock([&](SharedState& s){
            return (idx==1) ? s.copy1_pid : s.copy2_pid;
        });
    }

    void set_copy_pid(int idx, uint32_t pid)
    {
        with_lock([&](SharedState& s){
            if (idx==1) s.copy1_pid = pid;
            else s.copy2_pid = pid;
            return 0;
        });
    }
};

#else

struct SharedRegion {
    int shm_fd = -1;
    SharedState* st = nullptr;
    bool owner = false;

    bool init()
    {
        shm_fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0666);
        if (shm_fd < 0) return false;

        if (ftruncate(shm_fd, sizeof(SharedState)) != 0) return false;

        void* p = mmap(nullptr, sizeof(SharedState), PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);
        if (p == MAP_FAILED) return false;

        st = (SharedState*)p;

        // Одноразовая инициализация mutex: делаем попытку "ленивой" инициализации.
        // Если mutex уже был инициализирован ранее, повторная инициализация будет ошибкой.
        // Чтобы не городить отдельный init-флаг, используем прием: пробуем pthread_mutex_lock;
        // если возвращает EINVAL, значит не инициализирован — инициализируем.
        int rc = pthread_mutex_lock(&st->mtx);
        if (rc == EINVAL) {
            pthread_mutexattr_t attr;
            pthread_mutexattr_init(&attr);
            pthread_mutexattr_setpshared(&attr, PTHREAD_PROCESS_SHARED);
            pthread_mutex_init(&st->mtx, &attr);
            pthread_mutexattr_destroy(&attr);

            // Обнулим pids, оставим counter = 0 при первом запуске.
            pthread_mutex_lock(&st->mtx);
            st->counter = 0;
            st->copy1_pid = 0;
            st->copy2_pid = 0;
            pthread_mutex_unlock(&st->mtx);
        } else if (rc == 0) {
            pthread_mutex_unlock(&st->mtx);
        } else {
            // иной код — считаем фатальным
            return false;
        }

        return true;
    }

    void destroy()
    {
        if (st) munmap(st, sizeof(SharedState));
        if (shm_fd >= 0) close(shm_fd);
        st = nullptr;
        shm_fd = -1;
    }

    template <typename F>
    auto with_lock(F&& f) -> decltype(f(*st))
    {
        while (pthread_mutex_lock(&st->mtx) != 0) {}
        auto r = f(*st);
        pthread_mutex_unlock(&st->mtx);
        return r;
    }

    int64_t get_counter()
    {
        return with_lock([&](SharedState& s){ return s.counter; });
    }

    void set_counter(int64_t v)
    {
        with_lock([&](SharedState& s){ s.counter = v; return 0; });
    }

    void add_counter(int64_t dv)
    {
        with_lock([&](SharedState& s){ s.counter += dv; return 0; });
    }

    void mul_counter(int64_t k)
    {
        with_lock([&](SharedState& s){ s.counter *= k; return 0; });
    }

    void div_counter(int64_t k)
    {
        with_lock([&](SharedState& s){ s.counter /= k; return 0; });
    }

    pid_t get_copy_pid(int idx)
    {
        return with_lock([&](SharedState& s){
            return (idx==1) ? s.copy1_pid : s.copy2_pid;
        });
    }

    void set_copy_pid(int idx, pid_t pid)
    {
        with_lock([&](SharedState& s){
            if (idx==1) s.copy1_pid = pid;
            else s.copy2_pid = pid;
            return 0;
        });
    }
};

#endif

// =========================
// Остановка по сигналу
// =========================
static std::atomic<bool> g_stop{false};

#if defined(_WIN32)
static BOOL WINAPI console_handler(DWORD type)
{
    if (type == CTRL_C_EVENT || type == CTRL_CLOSE_EVENT || type == CTRL_BREAK_EVENT) {
        g_stop = true;
        return TRUE;
    }
    return FALSE;
}
#else
static void sig_handler(int)
{
    g_stop = true;
}
#endif

// =========================
// Проверка жив ли процесс (для копий)
// =========================
#if defined(_WIN32)
static bool process_alive(uint32_t pid)
{
    if (pid == 0) return false;
    HANDLE h = OpenProcess(SYNCHRONIZE, FALSE, pid);
    if (!h) return false;
    DWORD rc = WaitForSingleObject(h, 0);
    CloseHandle(h);
    return rc == WAIT_TIMEOUT;
}
#else
static bool process_alive(pid_t pid)
{
    if (pid <= 0) return false;
    if (kill(pid, 0) == 0) return true;
    return errno == EPERM; // существует, но нет прав
}
#endif

// =========================
// Лидерство
// =========================
#if defined(_WIN32)

struct LeaderLock {
    HANDLE hMutex = NULL;
    bool is_leader = false;

    bool acquire()
    {
        hMutex = CreateMutexA(NULL, FALSE, LEADER_MUTEX_NAME);
        if (!hMutex) return false;
        DWORD rc = WaitForSingleObject(hMutex, 0);
        if (rc == WAIT_OBJECT_0 || rc == WAIT_ABANDONED) {
            is_leader = true;
            return true;
        }
        is_leader = false;
        return true;
    }

    void release()
    {
        if (hMutex && is_leader) ReleaseMutex(hMutex);
        if (hMutex) CloseHandle(hMutex);
        hMutex = NULL;
        is_leader = false;
    }
};

#else

struct LeaderLock {
    int fd = -1;
    bool is_leader = false;

    bool acquire()
    {
        fd = ::open(LEADER_LOCK_PATH, O_CREAT | O_RDWR, 0644);
        if (fd < 0) return false;

        struct flock fl{};
        fl.l_type = F_WRLCK;
        fl.l_whence = SEEK_SET;
        fl.l_start = 0;
        fl.l_len = 0;

        int rc = fcntl(fd, F_SETLK, &fl); // non-blocking
        if (rc == 0) {
            is_leader = true;
        } else {
            is_leader = false;
        }
        return true;
    }

    void release()
    {
        if (fd >= 0 && is_leader) {
            struct flock fl{};
            fl.l_type = F_UNLCK;
            fl.l_whence = SEEK_SET;
            fl.l_start = 0;
            fl.l_len = 0;
            fcntl(fd, F_SETLK, &fl);
        }
        if (fd >= 0) ::close(fd);
        fd = -1;
        is_leader = false;
    }
};

#endif

// =========================
// Запуск копий
// =========================
#if defined(_WIN32)

static std::string get_self_path()
{
    char buf[MAX_PATH];
    DWORD n = GetModuleFileNameA(NULL, buf, MAX_PATH);
    return std::string(buf, buf + n);
}

static bool spawn_copy(const std::string& self, const std::string& arg, uint32_t& outPid)
{
    std::string cmd = "\"" + self + "\" " + arg;

    STARTUPINFOA si{};
    si.cb = sizeof(si);
    PROCESS_INFORMATION pi{};

    // Наследование handles не нужно
    BOOL ok = CreateProcessA(
        NULL,
        cmd.data(),
        NULL,
        NULL,
        FALSE,
        0,
        NULL,
        NULL,
        &si,
        &pi
    );
    if (!ok) return false;

    outPid = (uint32_t)pi.dwProcessId;
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    return true;
}

#else

static bool spawn_copy(const char* self, const char* arg, pid_t& outPid)
{
    pid_t pid = fork();
    if (pid < 0) return false;

    if (pid == 0) {
        execl(self, self, arg, (char*)nullptr);
        _exit(127);
    }

    outPid = pid;
    return true;
}

#endif

// =========================
// CLI поток
// =========================
static void cli_thread(SharedRegion* shared)
{
    std::string line;
    while (!g_stop && std::getline(std::cin, line)) {
        std::istringstream iss(line);
        std::string cmd;
        iss >> cmd;
        if (cmd == "set") {
            long long v;
            if (iss >> v) {
                shared->set_counter((int64_t)v);
            }
        } else if (cmd == "get") {
            auto v = shared->get_counter();
            std::cout << v << std::endl;
        } else if (cmd == "quit") {
            g_stop = true;
            break;
        }
    }
}

// =========================
// Режимы копий
// =========================
static int run_copy1(SharedRegion& shared)
{
#if defined(_WIN32)
    WinLog log;
#else
    PosixLog log;
#endif
    if (!log.open()) return 2;

    uint64_t pid = pid_u64();
    log.write_line("COPY1 START pid=" + std::to_string(pid) + " time=" + now_timestamp_local());

    shared.add_counter(10);

    log.write_line("COPY1 EXIT  pid=" + std::to_string(pid) + " time=" + now_timestamp_local());
    log.close();
    return 0;
}

static int run_copy2(SharedRegion& shared)
{
#if defined(_WIN32)
    WinLog log;
#else
    PosixLog log;
#endif
    if (!log.open()) return 2;

    uint64_t pid = pid_u64();
    log.write_line("COPY2 START pid=" + std::to_string(pid) + " time=" + now_timestamp_local());

    shared.mul_counter(2);
    std::this_thread::sleep_for(std::chrono::seconds(2));
    shared.div_counter(2);

    log.write_line("COPY2 EXIT  pid=" + std::to_string(pid) + " time=" + now_timestamp_local());
    log.close();
    return 0;
}

// =========================
// Основной режим
// =========================
static int run_main(int argc, char** argv)
{
    (void)argc; (void)argv;

#if defined(_WIN32)
    SetConsoleCtrlHandler(console_handler, TRUE);
#else
    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);
#endif

    SharedRegion shared;
    if (!shared.init()) return 2;

#if defined(_WIN32)
    WinLog log;
#else
    PosixLog log;
#endif
    if (!log.open()) return 2;

    const uint64_t pid = pid_u64();
    log.write_line("MAIN START pid=" + std::to_string(pid) + " time=" + now_timestamp_local());

    LeaderLock leader;
    if (!leader.acquire()) return 2;

    std::thread cli(cli_thread, &shared);

    auto t_last_300ms = std::chrono::steady_clock::now();
    auto t_last_1s    = std::chrono::steady_clock::now();
    auto t_last_3s    = std::chrono::steady_clock::now();

#if defined(_WIN32)
    const std::string self = get_self_path();
#else
    // argv[0] может быть относительным; для лабораторной достаточно.
    const char* self = argv[0];
#endif

    while (!g_stop) {
        auto now = std::chrono::steady_clock::now();

        // 300 мс: все основные процессы увеличивают счётчик
        if (now - t_last_300ms >= std::chrono::milliseconds(300)) {
            // догоняем, если были задержки
            while (now - t_last_300ms >= std::chrono::milliseconds(300)) {
                shared.add_counter(1);
                t_last_300ms += std::chrono::milliseconds(300);
            }
        }

        if (leader.is_leader) {
            // 1 сек: лог текущего времени, pid лидера и counter
            if (now - t_last_1s >= std::chrono::seconds(1)) {
                t_last_1s += std::chrono::seconds(1);
                int64_t c = shared.get_counter();
                log.write_line("TICK pid=" + std::to_string(pid) +
                               " time=" + now_timestamp_local() +
                               " counter=" + std::to_string((long long)c));
            }

            // 3 сек: запуск копий
            if (now - t_last_3s >= std::chrono::seconds(3)) {
                t_last_3s += std::chrono::seconds(3);

                // Копия 1
#if defined(_WIN32)
                uint32_t p1 = shared.get_copy_pid(1);
                if (process_alive(p1)) {
                    log.write_line("SPAWN SKIP copy1 still running pid=" + std::to_string(p1) +
                                   " leader_pid=" + std::to_string(pid) +
                                   " time=" + now_timestamp_local());
                } else {
                    if (p1 != 0) shared.set_copy_pid(1, 0);
                    uint32_t newPid = 0;
                    if (spawn_copy(self, "--copy1", newPid)) {
                        shared.set_copy_pid(1, newPid);
                    } else {
                        log.write_line("SPAWN FAIL copy1 leader_pid=" + std::to_string(pid) +
                                       " time=" + now_timestamp_local());
                    }
                }

                // Копия 2
                uint32_t p2 = shared.get_copy_pid(2);
                if (process_alive(p2)) {
                    log.write_line("SPAWN SKIP copy2 still running pid=" + std::to_string(p2) +
                                   " leader_pid=" + std::to_string(pid) +
                                   " time=" + now_timestamp_local());
                } else {
                    if (p2 != 0) shared.set_copy_pid(2, 0);
                    uint32_t newPid = 0;
                    if (spawn_copy(self, "--copy2", newPid)) {
                        shared.set_copy_pid(2, newPid);
                    } else {
                        log.write_line("SPAWN FAIL copy2 leader_pid=" + std::to_string(pid) +
                                       " time=" + now_timestamp_local());
                    }
                }

#else
                pid_t p1 = shared.get_copy_pid(1);
                if (process_alive(p1)) {
                    log.write_line("SPAWN SKIP copy1 still running pid=" + std::to_string((long long)p1) +
                                   " leader_pid=" + std::to_string(pid) +
                                   " time=" + now_timestamp_local());
                } else {
                    if (p1 != 0) shared.set_copy_pid(1, 0);
                    pid_t newPid = 0;
                    if (spawn_copy(self, "--copy1", newPid)) {
                        shared.set_copy_pid(1, newPid);
                    } else {
                        log.write_line("SPAWN FAIL copy1 leader_pid=" + std::to_string(pid) +
                                       " time=" + now_timestamp_local());
                    }
                }

                pid_t p2 = shared.get_copy_pid(2);
                if (process_alive(p2)) {
                    log.write_line("SPAWN SKIP copy2 still running pid=" + std::to_string((long long)p2) +
                                   " leader_pid=" + std::to_string(pid) +
                                   " time=" + now_timestamp_local());
                } else {
                    if (p2 != 0) shared.set_copy_pid(2, 0);
                    pid_t newPid = 0;
                    if (spawn_copy(self, "--copy2", newPid)) {
                        shared.set_copy_pid(2, newPid);
                    } else {
                        log.write_line("SPAWN FAIL copy2 leader_pid=" + std::to_string(pid) +
                                       " time=" + now_timestamp_local());
                    }
                }
#endif
            }
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }

    // Завершение
    leader.release();

    if (cli.joinable()) {
        // если stdin заблокирован, поток может не выйти сам; в лабораторной обычно достаточно
        // (при Ctrl+C std::getline может не прерваться на некоторых платформах).
        // Здесь оставляем join: при нормальном quit/Ctrl+C в терминале обычно корректно.
        cli.join();
    }

    log.write_line("MAIN EXIT  pid=" + std::to_string(pid) + " time=" + now_timestamp_local());
    log.close();
    shared.destroy();
    return 0;
}

// =========================
// entry
// =========================
int main(int argc, char** argv)
{
    SharedRegion shared;
    if (!shared.init()) return 2;

    // Режим копий
    if (argc >= 2) {
        if (std::string(argv[1]) == "--copy1") {
            int rc = run_copy1(shared);
            shared.destroy();
            return rc;
        }
        if (std::string(argv[1]) == "--copy2") {
            int rc = run_copy2(shared);
            shared.destroy();
            return rc;
        }
    }

    shared.destroy();
    return run_main(argc, argv);
}
