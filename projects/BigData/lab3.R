# Загрузка необходимых библиотек
library(ggplot2)
library(caret)
library(kernlab)

# 1. Прочитать файл
setwd("/Users/daniil/Desktop/Обучение/BigData/datasets")
dd <- read.table(file='flsr_moscow.txt', header=TRUE)

# 2. Очистка данных: удаление строк с пропущенными значениями
dim(dd)
dd_clean <- na.omit(dd)
dd_clean <- dd_clean[-4:-11]  # удаляем неиспользуемые переменные
dim(dd_clean)

# 3. Создать факторную переменную target
dd_clean$target <- factor(ifelse(dd_clean$nrooms %in% c(1, 2), "1,2-комнатные квартиры", "3,4-комнатные квартиры"))

# 4. Разделение на выборки: тренировочная (70%), тестовая (15%), валидационная (15%)
set.seed(42)
train_idx <- sample(1:nrow(dd_clean), size = 0.7 * nrow(dd_clean))  # 70% на тренировочную
remaining_idx <- setdiff(1:nrow(dd_clean), train_idx)  # остаток

# Разделим оставшиеся 30% на тестовую и валидационную выборки
test_idx <- sample(remaining_idx, size = 0.5 * length(remaining_idx))  # 15% на тестовую
validation_idx <- setdiff(remaining_idx, test_idx)  # оставшиеся 15% на валидационную

train_data <- dd_clean[train_idx, ]
test_data <- dd_clean[test_idx, ]
validation_data <- dd_clean[validation_idx, ]

# 5. Построение модели логистической регрессии
log_reg_model <- glm(target ~ price + totsp, data=train_data, family="binomial")

# 6. Оценка модели логистической регрессии на тестовой выборке
log_reg_test_predictions <- predict(log_reg_model, newdata=test_data, type="response")
log_reg_test_predicted_class <- ifelse(log_reg_test_predictions > 0.5, "3,4-комнатные квартиры", "1,2-комнатные квартиры")

# Оценка точности модели логистической регрессии на тестовой выборке
log_reg_test_conf_matrix <- confusionMatrix(factor(log_reg_test_predicted_class), test_data$target)
print("Confusion Matrix для логистической регрессии на тестовой выборке:")
print(log_reg_test_conf_matrix)

# 7. Построение модели SVM (метод опорных векторов)
svm_model <- ksvm(target ~ price + totsp, data=train_data, kernel="rbfdot", C=1)

# 8. Оценка модели SVM на тестовой выборке
svm_test_predictions <- predict(svm_model, newdata=test_data)
svm_test_conf_matrix <- confusionMatrix(factor(svm_test_predictions), test_data$target)
print("Confusion Matrix для модели SVM на тестовой выборке:")
print(svm_test_conf_matrix)

# 9. Оценка модели на валидационной выборке (для обеих моделей)

# Логистическая регрессия на валидационной выборке
log_reg_validation_predictions <- predict(log_reg_model, newdata=validation_data, type="response")
log_reg_validation_predicted_class <- ifelse(log_reg_validation_predictions > 0.5, "3,4-комнатные квартиры", "1,2-комнатные квартиры")
log_reg_validation_conf_matrix <- confusionMatrix(factor(log_reg_validation_predicted_class), validation_data$target)
print("Confusion Matrix для логистической регрессии на валидационной выборке:")
print(log_reg_validation_conf_matrix)

# SVM на валидационной выборке
svm_validation_predictions <- predict(svm_model, newdata=validation_data)
svm_validation_conf_matrix <- confusionMatrix(factor(svm_validation_predictions), validation_data$target)
print("Confusion Matrix для модели SVM на валидационной выборке:")
print(svm_validation_conf_matrix)

# 10. Визуализация
# График распределения цен по количеству комнат
ggplot(dd_clean, aes(x=target, y=price, fill=target)) +
  geom_boxplot() +
  labs(title="Распределение цен по количеству комнат", x="Тип квартиры", y="Цена") +
  theme_minimal()

# График зависимости цены от общей площади квартиры
ggplot(dd_clean, aes(x=price, y=totsp, color=target)) + 
  geom_point() +
  labs(title="Визуализация задачи классификации", x="Цена", y="Общая площадь") +
  theme_minimal()
