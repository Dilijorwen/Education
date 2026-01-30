#pragma once
#include <cstdint>

struct RollingAgg {
    int64_t bucket_start_ms = 0;
    double sum = 0.0;
    int64_t count = 0;

    void reset(int64_t new_bucket_start_ms) {
        bucket_start_ms = new_bucket_start_ms;
        sum = 0.0;
        count = 0;
    }

    void add(double v) {
        sum += v;
        count += 1;
    }

    double avg() const {
        return (count > 0) ? (sum / static_cast<double>(count)) : 0.0;
    }
};
