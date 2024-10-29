library(dplyr)
library(ggplot2)

# Загрузка данных
diamond <- read.csv(file = "rand5.csv", header = TRUE, sep = ",")
str(diamond)
# Вывод размерности до очистки
cat("Размерность до чистки:", dim(diamond), "\n")
head(diamond)

# Удаление пропусков
diamond <- na.omit(diamond)

# Вывод размерности после очистки
cat("Размерность после чистки:", dim(diamond), "\n")
head(diamond)

# Вывод уникальных значений столбца color
unique(diamond$color)

# Пересылаем два последних(два самых ходших значения в толбце color)
worst_colors <- unique(diamond$color)[6:7]

# Вывод уникальных значений столбца cut
unique(diamond$cut)

# Пересылаем два последних(два самых ходших значения в толбце cut)
worst_cuts <- unique(diamond$cut)[4:5]

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
  geom_histogram(binwidth = 0.1, position = "dodge") +
  labs(title = "Distribution of Diamond Carat by Color and Cut",
       x = "Carat",
       y = "Count") +
  scale_fill_discrete(name = "Color and Cut") +
  theme_minimal()


ggplot(subset, aes(x = price, fill = interaction(color, cut))) +
  geom_histogram(binwidth = 500, position = "dodge") +
  labs(title = "Distribution of Diamond Price by Color and Cut",
       x = "Price",
       y = "Count") +
  scale_fill_discrete(name = "Color and Cut") +
  theme_minimal()

