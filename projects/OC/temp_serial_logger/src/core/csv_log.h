#pragma once
#include <cstdint>
#include <functional>
#include <string>

namespace csvlog {

    // создаёт файл и пишет header, если файла нет
    void ensure_with_header(const std::string& path, const std::string& header);

    // дописывает строку (с '\n')
    void append_line(const std::string& path, const std::string& line);

    // переписывает файл, оставляя header и строки, для которых keep(line)==true
    // keep получает сырой line без '\n'
    void prune_keep_lines(
        const std::string& path,
        const std::string& header,
        const std::function<bool(const std::string&)>& keep
    );

} // namespace csvlog
