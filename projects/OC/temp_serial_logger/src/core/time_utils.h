#pragma once
#include <cstdint>
#include <string>

namespace timeu {

    int64_t now_epoch_ms();

    int64_t floor_to_hour_utc_ms(int64_t epoch_ms);
    int64_t floor_to_day_utc_ms(int64_t epoch_ms);

    int64_t start_of_year_utc_ms(int64_t epoch_ms);

    std::string to_string_utc(int64_t epoch_ms);

}

