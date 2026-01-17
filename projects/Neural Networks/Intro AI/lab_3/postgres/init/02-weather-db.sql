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

CREATE TABLE IF NOT EXISTS weather_inference_metrics (
  id            BIGSERIAL PRIMARY KEY,
  calculated_at TIMESTAMPTZ NOT NULL,

  city          TEXT NOT NULL,
  observed_time TIMESTAMP NOT NULL,
  rule_version  TEXT NOT NULL,

  ok            BOOLEAN NOT NULL,
  condition     TEXT NOT NULL,
  severity      INTEGER NOT NULL,
  tags          JSONB NOT NULL DEFAULT '[]'::jsonb
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_weather_inference_metrics_city_time_rule
  ON weather_inference_metrics(city, observed_time, rule_version);

