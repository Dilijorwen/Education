#include "csv_log.h"

#include <filesystem>
#include <fstream>
#include <string>

namespace csvlog {

    void ensure_with_header(const std::string& path, const std::string& header) {
        if (std::filesystem::exists(path)) return;
        std::filesystem::create_directories(std::filesystem::path(path).parent_path());
        std::ofstream out(path, std::ios::binary);
        out << header << "\n";
    }

    void append_line(const std::string& path, const std::string& line) {
        std::filesystem::create_directories(std::filesystem::path(path).parent_path());
        std::ofstream out(path, std::ios::binary | std::ios::app);
        out << line << "\n";
    }

    void prune_keep_lines(
        const std::string& path,
        const std::string& header,
        const std::function<bool(const std::string&)>& keep
    ) {
        namespace fs = std::filesystem;
        if (!fs::exists(path)) {
            ensure_with_header(path, header);
            return;
        }

        const fs::path p(path);
        const fs::path tmp = p.parent_path() / (p.filename().string() + ".tmp");

        std::ifstream in(path, std::ios::binary);
        std::ofstream out(tmp.string(), std::ios::binary | std::ios::trunc);

        out << header << "\n";

        std::string line;
        bool first = true;
        while (std::getline(in, line)) {
            if (first) { // пропускаем старый header
                first = false;
                continue;
            }
            if (!line.empty() && keep(line)) out << line << "\n";
        }


        in.close();
        out.close();

#if defined(_WIN32)
        // на Windows rename поверх существующего может падать
        fs::remove(p);
        fs::rename(tmp, p);
#else
        fs::rename(tmp, p);
#endif
    }

} // namespace csvlog
