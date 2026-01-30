#include "exe_path.h"

#include <filesystem>

#if defined(_WIN32)
  #ifndef NOMINMAX
  #define NOMINMAX
  #endif
  #include <windows.h>
#elif defined(__APPLE__)
  #include <mach-o/dyld.h>
  #include <vector>
#else
  #include <unistd.h>
  #include <vector>
#endif

namespace exe_path {

    std::filesystem::path executable_dir() {
        namespace fs = std::filesystem;

#if defined(_WIN32)
        std::wstring buf(32768, L'\0');
        DWORD n = GetModuleFileNameW(nullptr, buf.data(), (DWORD)buf.size());
        buf.resize(n);
        return fs::path(buf).parent_path();

#elif defined(__APPLE__)
        uint32_t size = 0;
        _NSGetExecutablePath(nullptr, &size);
        std::vector<char> buf(size);
        if (_NSGetExecutablePath(buf.data(), &size) == 0) {
            std::error_code ec;
            fs::path p = fs::weakly_canonical(fs::path(buf.data()), ec);
            if (ec) p = fs::path(buf.data());
            return p.parent_path();
        }
        return fs::current_path();

#else
        std::vector<char> buf(4096);
        ssize_t n = readlink("/proc/self/exe", buf.data(), buf.size() - 1);
        if (n > 0) {
            buf[(size_t)n] = '\0';
            std::error_code ec;
            fs::path p = fs::weakly_canonical(fs::path(buf.data()), ec);
            if (ec) p = fs::path(buf.data());
            return p.parent_path();
        }
        return fs::current_path();
#endif
    }

} // namespace exe_path
