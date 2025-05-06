library(ggplot2)

# Ставим рабочую дирректорию для R
setwd("/Users/daniil/Desktop/Обучение/BigData/datasets")

# Загрузка данных
diamond <- read.csv(file = "rand5.csv", header = TRUE, sep = ",")
# Вывод размерности до очистки
cat("Размерность до чистки:", dim(diamond), "\n")

# Удаление пропусков
diamond <- na.omit(diamond)

# Вывод размерности после очистки
cat("Размерность после чистки:", dim(diamond), "\n")
head(diamond)

# Вывод уникальных ord factor значений столбца color
unique(diamond$color)

# Пересылаем два самых ходших значения в толбце color
worst_colors <- sort(unique(diamonds$color))[1:2]


# Вывод уникальных ord factor значений столбца cut
sort(unique(diamonds$cut))

# Пересылаем два самых ходших значения в толбце cut
worst_cuts <- sort(unique(diamonds$cut))[1:2]


# Создаем subset под нужные требования
subset <- diamond[(diamond$cut %in% worst_cuts) & (diamond$color %in% worst_colors), ]

# Считаем все данные указзынные в задании
summary <- data.frame(
  Mean_price = mean(subset$price),
  Var_price = var(subset$price),
  Mean_weight = mean(subset$carat),
  Var_weight = var(subset$carat)
)
summary

# Рисуем графики
ggplot(subset, aes(x = carat, fill = interaction(color, cut))) +
  geom_histogram(binwidth = 0.1, position = "stack") +
  labs(title = "Distribution of Diamond Carat by Color and Cut",
       x = "Carat",
       y = "Count") +
  scale_fill_discrete(name = "Color and Cut") +
  theme_minimal()


ggplot(subset, aes(x = price, fill = interaction(color, cut))) +
  geom_histogram(binwidth = 500, position = "stack") +
  labs(title = "Distribution of Diamond Price by Color and Cut",
       x = "Price",
       y = "Count") +
  scale_fill_discrete(name = "Color and Cut") +
  theme_minimal()

