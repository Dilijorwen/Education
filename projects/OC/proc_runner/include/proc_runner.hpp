#pragma once
#include <cstdint>
#include <string>
#include <vector>
#include <optional>

namespace proc_runner {

// Результат ожидания
enum class WaitStatus {
    Exited,     // процесс завершился, exit_code заполнен
    StillRunning,
    Failed
};

struct WaitResult {
    WaitStatus status{WaitStatus::Failed};
    int exit_code{-1}; // валиден только при Exited
};

// Кроссплатформенный дескриптор процесса
class Process {
public:
    Process() = default;
    ~Process();

    Process(const Process&) = delete;
    Process& operator=(const Process&) = delete;

    Process(Process&& other) noexcept;
    Process& operator=(Process&& other) noexcept;

    // Возвращает "pid" (Windows: PID, POSIX: pid)
    std::uint32_t pid() const;

    // Проверка, жив ли процесс (не блокирует)
    bool is_running() const;

    // Дождаться завершения без таймаута (блокирует)
    // Возвращает: {Exited, code} либо {Failed, -1}
    WaitResult wait();

    // Дождаться завершения с таймаутом (миллисекунды)
    // timeout_ms == 0 -> не ждать (poll)
    // timeout_ms < 0  -> ждать бесконечно
    WaitResult wait_for(int timeout_ms);

    // Принудительно завершить
    bool terminate();

    // Валидность объекта процесса
    bool valid() const;

private:
#ifdef _WIN32
    void* hProcess_{nullptr};
    void* hThread_{nullptr};
    std::uint32_t pid_{0};
#else
    int pid_{-1};
#endif
    bool owns_{false};

    friend std::optional<Process> spawn(
        const std::string& program,
        const std::vector<std::string>& args,
        const std::optional<std::string>& working_dir
    );
};

// Запуск процесса в фоновом режиме.
// program: путь к исполняемому файлу или имя, которое найдётся в PATH.
// args: аргументы (без program).
// working_dir: опциональная рабочая директория.
//
// Возвращает Process при успехе, иначе std::nullopt.
std::optional<Process> spawn(
    const std::string& program,
    const std::vector<std::string>& args = {},
    const std::optional<std::string>& working_dir = std::nullopt
);

} // namespace proc_runner
