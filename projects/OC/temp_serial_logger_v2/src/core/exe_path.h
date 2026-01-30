#pragma once
#include <filesystem>

namespace exe_path {
    // директория, где лежит текущий exe
    std::filesystem::path executable_dir();
}
