#!/usr/bin/env Rscript
# シェアサイクル合成データの生成スクリプト
# 実行: Rscript src/generate_data.R

pacman::p_load(tidyverse)

set.seed(42)
n_days <- 365
hours <- 0:23

bike_data <- expand_grid(
  date = as.Date("2024-01-01") + 0:(n_days - 1),
  hour = hours
) |>
  mutate(
    month = month(date),
    wday = wday(date, label = TRUE, locale = "C"),
    is_weekend = wday %in% c("Sat", "Sun"),
    temperature = 15 + 12 * sin((month - 4) * pi / 6) + rnorm(n(), 0, 3),
    humidity = 60 + 15 * sin((month - 7) * pi / 6) + rnorm(n(), 0, 8),
    humidity = pmin(pmax(humidity, 20), 100),
    wind_speed = rgamma(n(), shape = 2, rate = 0.8),
    is_rain = rbinom(n(), 1, prob = ifelse(month %in% 6:9, 0.25, 0.12)),
    hour_effect = case_when(
      hour %in% 7:9   ~ 1.8,
      hour %in% 12:13  ~ 1.3,
      hour %in% 17:19  ~ 2.0,
      hour %in% 22:5   ~ 0.3,
      TRUE             ~ 1.0
    ),
    temp_effect = pmax(0.5, 1 + (temperature - 15) * 0.03),
    rain_effect = ifelse(is_rain == 1, 0.4, 1.0),
    weekend_effect = ifelse(is_weekend, 0.75, 1.0),
    base_count = 80 * hour_effect * temp_effect * rain_effect * weekend_effect,
    count = as.integer(pmax(0, base_count + rnorm(n(), 0, 15)))
  ) |>
  select(date, hour, month, wday, is_weekend,
         temperature, humidity, wind_speed, is_rain, count)

write_csv(bike_data, "data/bike_data.csv")
cat("Generated:", nrow(bike_data), "rows -> data/bike_data.csv\n")
