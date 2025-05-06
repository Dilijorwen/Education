# Подключение библиотеки ggplot2
library(ggplot2)

# Установка рабочей директории
setwd("/Users/daniil/Desktop/Обучение/BigData/datasets")

# Загрузка данных из файла
diamonds <- read.csv(file = "rand5.csv", header = TRUE, sep = ",")

#Проверка на существованиние Nan элементов diamonds
anyNA(diamonds)

# Вывод первых строк датасета для проверки его корректности 
head(diamonds)

# Выводим уникальные значения столбца color и выбираем два худших
sort(unique(diamonds$color))
worst_colors <- sort(unique(diamonds$color))[1:2]
worst_colors

# Выводим уникальные значения столбца cut и выбираем два худших
sort(unique(diamonds$cut))
worst_cuts <- sort(unique(diamonds$cut))[1:2]
worst_cuts

# Создаем подмножество данных, соответствующее выбранным условиям
subset <- diamonds[(diamonds$cut %in% worst_cuts) & 
                     (diamonds$color %in% worst_colors), ]

#Проверка на существованиние Nan элементов в subset


# Вывод первых строк подмножества для проверки корректности фильтрации
head(subset)

# Построение линейной модели, где price - зависимая переменная, а carat - регрессор
lm <- lm(price ~ carat, data = subset)

# Выводим сводку модели
s <- summary(lm)
s

# Вычисляем максимальный вес (carat) в подмножестве
max_carat <- max(subset$carat)
max_carat

# Увеличиваем максимальный вес на 5%, 10%, 15% для прогнозирования
max_carats <- max_carat * c(1.05, 1.10, 1.15)
max_carats

# Создаем новый датафрейм для прогнозов
new_data <- data.frame(carat = max_carats)
new_data

# Точечные прогнозы
point_predictions <- predict(lm, newdata = new_data)

# Прогнозы с предиктивными и доверительными интервалами
predictions_pred <- predict(lm, newdata = new_data, 
                            interval = "prediction", level = 0.95)[, -1]
predictions_conf <- predict(lm, newdata = new_data, 
                            interval = "confidence", level = 0.95)[, -1]

results_table <- data.frame(
  Carat = new_data$carat,
  Point_Pred = point_predictions,
  Pred_Lwr = predictions_pred[, "lwr"],
  Pred_Upr = predictions_pred[, "upr"],
  Conf_Lwr = predictions_conf[, "lwr"],
  Conf_Upr = predictions_conf[, "upr"]
)

results_table


# Создаем последовательность значений веса для построения графика
carat_range <- subset$carat
head(carat_range)

# Создаем датафрейм для визуализации
plot_data <- data.frame(carat = carat_range)


head(plot_data)


# Получаем прогнозы для визуализации с доверительным интервалом
visual_predictions_conf <- predict(lm, newdata = plot_data, interval = "confidence", level = 0.95)
visual_predictions_conf <- as.data.frame(visual_predictions_conf)
visual_predictions_conf$carat <- carat_range
visual_predictions_conf$IntervalType <- "Доверительный интервал"

# Получаем прогнозы для визуализации с предиктивным интервалом
visual_predictions_pred <- predict(lm, newdata = plot_data, interval = "prediction", level = 0.95)
visual_predictions_pred <- as.data.frame(visual_predictions_pred)
visual_predictions_pred$carat <- carat_range
visual_predictions_pred$IntervalType <- "Предиктивный интервал"

# Объединяем доверительный и предиктивный интервалы в один датафрейм
combined_predictions <- rbind(
  visual_predictions_conf[, c("carat", "lwr", "upr", "IntervalType")],
  visual_predictions_pred[, c("carat", "lwr", "upr", "IntervalType")]
)

# Строим график модели линейной регрессии с доверительным и предиктивным интервалами
ggplot(subset, aes(x = carat, y = price)) +
  geom_point(color = "blue") +  # Исходные данные
  geom_line(data = visual_predictions_conf, aes(x = carat, y = fit), color = "red") +  # Линия регрессии
  geom_ribbon(data = combined_predictions, 
              aes(x = carat, ymin = lwr, ymax = upr, fill = IntervalType), 
              alpha = 0.2, inherit.aes = FALSE) +  # Доверительный и предиктивный интервалы
  labs(title = "Модель линейной регрессии: Цена vs Вес",
       subtitle = "С доверительным и предиктивным интервалами",
       x = "Вес (карат)",
       y = "Цена (USD)",
       fill = "Тип интервала") +  # Заголовок легенды
  scale_fill_manual(values = c("Доверительный интервал" = "green", 
                               "Предиктивный интервал" = "orange")) +  # Цвета интервалов
  theme_minimal() +
  theme(legend.position = "right")  # Размещение легенды справа