\connect weather;

CREATE TABLE IF NOT EXISTS weather_inference (
  id            BIGSERIAL PRIMARY KEY,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),

  city          TEXT NOT NULL,
  observed_time TIMESTAMP NOT NULL,
  rule_version  TEXT NOT NULL,

  condition     TEXT NOT NULL,
  severity      INTEGER NOT NULL,
  tags          JSONB NOT NULL DEFAULT '[]'::jsonb,

  payload       JSONB NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_weather_inference_city_time_rule
  ON weather_inference(city, observed_time, rule_version);

CREATE INDEX IF NOT EXISTS idx_weather_inference_city_time
  ON weather_inference(city, observed_time);

CREATE INDEX IF NOT EXISTS idx_weather_inference_payload_gin
  ON weather_inference USING GIN (payload);
