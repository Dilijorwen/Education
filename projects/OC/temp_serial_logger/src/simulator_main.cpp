#include "core/time_utils.h"

#include <chrono>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <random>
#include <string>
#include <thread>

static std::string arg_value(int argc, char** argv, const std::string& key, const std::string& def) {
    for (int i = 1; i + 1 < argc; ++i) {
        if (argv[i] == key) return argv[i + 1];
    }
    return def;
}

int main(int argc, char** argv) {
    const int period_ms = std::stoi(arg_value(argc, argv, std::string("--period-ms"), std::string("1000")));
    const double base = std::stod(arg_value(argc, argv, std::string("--base"), std::string("23.0")));
    const double amp  = std::stod(arg_value(argc, argv, std::string("--amp"),  std::string("2.0")));
    const double noise = std::stod(arg_value(argc, argv, std::string("--noise"), std::string("0.2")));

    std::mt19937_64 rng{static_cast<uint64_t>(timeu::now_epoch_ms())};
    std::normal_distribution<double> n01(0.0, noise);

    while (true) {
        const int64_t t = timeu::now_epoch_ms();
        const double day_phase = std::sin((double)(t % 86'400'000LL) / 86'400'000.0 * 2.0 * 3.141592653589793);
        const double temp = base + amp * day_phase + n01(rng);

        // формат как у “устройства”: одно измерение в строке
        std::cout << temp << "\n";
        std::cout.flush();

        std::this_thread::sleep_for(std::chrono::milliseconds(period_ms));
    }
}
