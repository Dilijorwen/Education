CREATE DATABASE weather OWNER airflow;

\connect weather;

CREATE TABLE weather_current (
  id                 BIGSERIAL PRIMARY KEY,
  observed_time      TIMESTAMP,

  city               TEXT NOT NULL,

  timezone           TEXT,
  utc_offset_seconds INTEGER,
  elevation          DOUBLE PRECISION,

  temperature_2m     DOUBLE PRECISION,
  relative_humidity  INTEGER,
  is_day             INTEGER,
  precipitation_mm   DOUBLE PRECISION,
  wind_speed_10m     DOUBLE PRECISION,
  wind_direction_deg INTEGER,
  wind_gusts_10m     DOUBLE PRECISION,

  payload            JSONB NOT NULL
);


CREATE INDEX idx_weather_current_city ON weather_current(city);
CREATE INDEX idx_weather_current_payload_gin ON weather_current USING GIN (payload);


INSERT INTO weather_current (observed_time,
  city, timezone, utc_offset_seconds, elevation,
  temperature_2m, relative_humidity, is_day, precipitation_mm,
  wind_speed_10m, wind_direction_deg, wind_gusts_10m,
  payload
) VALUES ('2026-01-13T22:45'::timestamp,
  'Vladivostok', 'Asia/Vladivostok', 36000, 42.0,
  -13.7, 59, 0, 0.00,
  16.7, 307, 29.5,
  '{
    "latitude":43.125,
    "longitude":132.0,
    "generationtime_ms":0.07390975952148438,
    "utc_offset_seconds":36000,
    "timezone":"Asia/Vladivostok",
    "timezone_abbreviation":"GMT+10",
    "elevation":42.0,
    "current_units":{
      "time":"iso8601","interval":"seconds","temperature_2m":"°C",
      "relative_humidity_2m":"%","is_day":"","precipitation":"mm",
      "wind_speed_10m":"km/h","wind_direction_10m":"°",
      "wind_gusts_10m":"km/h"
    },
    "current":{
      "time":"2026-01-13T22:45","interval":900,"temperature_2m":-13.7,
      "relative_humidity_2m":59,"is_day":0,"precipitation":0.00,
      "wind_speed_10m":16.7,"wind_direction_10m":307,"wind_gusts_10m":29.5
    }
  }'::jsonb
);
