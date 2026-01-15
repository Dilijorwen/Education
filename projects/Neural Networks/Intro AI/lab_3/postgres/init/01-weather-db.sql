\connect weather;

ALTER TABLE weather_current
  ADD CONSTRAINT uq_weather_current_city_observed_time
  UNIQUE (city, observed_time);