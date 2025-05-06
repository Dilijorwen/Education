# ================================
# 1. Подключение библиотек и настройка
# ================================
library(caret)
library(dplyr)
library(VIM)
library(pROC)

# Установка рабочей директории (раскомментируйте, если требуется)
setwd("/Users/daniil/Desktop/Обучение/BigData/datasets")

# ================================
# 2. Загрузка и первоначальный осмотр данных
# ================================
titanic <- read.csv('titanic3.csv')

# Размер данных и количество пропусков по столбцам
dim(titanic)
titanic %>% summarise_all(~ sum(is.na(.)))
head(titanic)

# Выбираем только нужные столбцы
titanic <- titanic[, c("survived", "pclass", "sex", "age", "sibsp", "parch", "fare", "embarked")]

# ================================
# 3. Преобразование переменных и обработка пропусков
# ================================
# Преобразуем категориальные переменные
titanic$sex <- as.factor(titanic$sex)
titanic$pclass <- as.factor(titanic$pclass)

# Замена пропусков в embarked значением "S"
titanic$embarked[is.na(titanic$embarked)] <- "S"
titanic$embarked <- as.factor(titanic$embarked)

# Импутация пропусков в переменной age с помощью kNN (k = 5)
titanic <- kNN(titanic, variable = "age", k = 5)
titanic <- titanic[, !grepl("imp$", names(titanic))]

# Заполнение пропусков в fare медианным значением
titanic$fare[is.na(titanic$fare)] <- median(titanic$fare, na.rm = TRUE)

# Вывод статистики по возрасту и общий обзор данных
mean(titanic$age, na.rm = TRUE)
dim(titanic)
str(titanic)
head(titanic)
titanic %>% summarise_all(~ sum(is.na(.)))

# ================================
# 4. Разделение выборки на обучающую и тестовую
# ================================
set.seed(2005)
train_index <- createDataPartition(titanic$survived, p = 0.8, list = FALSE)
train_data <- titanic[train_index, ]
test_data <- titanic[-train_index, ]

# ================================
# 5. Построение и оптимизация логистической регрессии
# ================================
# Модель с полным набором переменных
full_model <- glm(survived ~ parch + fare + age + pclass + sex + sibsp, 
                  data = train_data, family = binomial)

# Удаление незначимых переменных методом backward
reduced_model <- step(full_model, direction = "backward", trace = TRUE)

# ================================
# 6. Оценка модели на тестовой выборке
# ================================
# Предсказание вероятностей выживания на тестовой выборке
test_data$predicted_survival <- predict(reduced_model, newdata = test_data, type = "response")

# Построение ROC-кривой и подбор оптимального порога
roc_obj <- roc(test_data$survived, test_data$predicted_survival)
optimal_threshold <- as.numeric(coords(roc_obj, "best", ret = "threshold", best.method = "closest.topleft"))
cat("Оптимальный порог:", optimal_threshold, "\n")

# Классификация наблюдений по оптимальному порогу
test_data$predicted_class <- ifelse(test_data$predicted_survival > optimal_threshold, 1, 0)

# Матрица ошибок и вычисление метрик
conf_matrix <- confusionMatrix(factor(test_data$predicted_class, levels = c(0, 1)), 
                               factor(test_data$survived, levels = c(0, 1)))

cat("Финальная модель:", deparse(formula(reduced_model)), "\n")
summary(reduced_model)
print(conf_matrix)
cat("Precision:", conf_matrix$byClass['Pos Pred Value'], "\n")
cat("Recall:", conf_matrix$byClass['Sensitivity'], "\n")

# ================================
# 7. Прогноз для мини-выборки и ручной расчёт
# ================================
mini_test_data <- data.frame(
  age = c(30, 22, 46, 32),
  pclass = factor(c("3rd", "2nd", "1st", "3rd"), levels = levels(titanic$pclass)),
  sex = factor(c("female", "male", "male", "female"), levels = levels(titanic$sex)),
  sibsp = c(0, 2, 1, 0)
)

# Предсказание вероятности и класса с помощью модели
mini_predicted_survival <- predict(reduced_model, newdata = mini_test_data, type = "response")
mini_predicted_class <- ifelse(mini_predicted_survival > 0.5, 1, 0)

# Ручной прогноз на основе коэффициентов модели
coefs <- coefficients(reduced_model)
logit <- coefs["(Intercept)"] + 
  coefs["age"] * mini_test_data$age + 
  coefs["sibsp"] * mini_test_data$sibsp + 
  ifelse(mini_test_data$pclass == "2nd", coefs["pclass2nd"], 0) + 
  ifelse(mini_test_data$pclass == "3rd", coefs["pclass3rd"], 0) + 
  ifelse(mini_test_data$sex == "male", coefs["sexmale"], 0)

mini_predicted_survival_hand <- 1 / (1 + exp(-logit))
mini_predicted_class_hand <- ifelse(mini_predicted_survival_hand > 0.5, 1, 0)

# Вывод результатов прогноза
cat("Прогнозируемый класс (0 - не выжил, 1 - выжил):", mini_predicted_class, "\n")
cat("Предсказанная вероятность выживания:", mini_predicted_survival, "\n")
cat("Ручной прогноз выживания (0 - не выжил, 1 - выжил):", mini_predicted_class_hand, "\n")
cat("Ручной расчет вероятности выживания:", mini_predicted_survival_hand, "\n")

# ================================
# 8. Анализ ошибок модели (FP и FN)
# ================================
# Ложно-положительные (FP) - предсказано "выжил", но реально "не выжил"
false_positives <- test_data[test_data$predicted_class == 1 & test_data$survived == 0, ]
false_positives_male <- test_data[test_data$predicted_class == 1 & test_data$survived == 0 & test_data$sex == "male", ]
false_positives_female <- test_data[test_data$predicted_class == 1 & test_data$survived == 0 & test_data$sex == "female", ]

# Ложно-отрицательные (FN) - предсказано "не выжил", но реально "выжил"
false_negatives <- test_data[test_data$predicted_class == 0 & test_data$survived == 1, ]
false_negatives_male <- test_data[test_data$predicted_class == 0 & test_data$survived == 1 & test_data$sex == "male", ]
false_negatives_female <- test_data[test_data$predicted_class == 0 & test_data$survived == 1 & test_data$sex == "female", ]

# Вывод сводной информации по FP и FN
print("False Positives for Male (FP)")
print(summary(false_positives_male))
print("False Positives for Female (FP)")
print(summary(false_positives_female))
print("False Negatives for Male (FN)")
print(summary(false_negatives_male))
print("False Negatives for Female (FN)")
print(summary(false_negatives_female))

# ================================
# 9. Логическая классификация ошибок по заданным условиям
# ================================
# Создание столбца error_type для идентификации ошибки
test_data$error_type <- ifelse(test_data$predicted_class == 1 & test_data$survived == 0, "FP",
                               ifelse(test_data$predicted_class == 0 & test_data$survived == 1, "FN",
                                      "Correct"))

# Инициализация столбца logical_class значением "Correct"
test_data$logical_class <- rep("Correct", nrow(test_data))

# Классификация ложно-положительных (FP)
fp_idx <- which(test_data$error_type == "FP")
# FP: Мужчины в возрасте от 20 до 40
male_fp <- fp_idx[test_data$sex[fp_idx] == "male" & test_data$age[fp_idx] >= 20 & test_data$age[fp_idx] <= 40]
test_data$logical_class[male_fp] <- "FP_male_20_40"
# FP: Женщины 3-го класса
female_fp <- fp_idx[test_data$sex[fp_idx] == "female" & test_data$pclass[fp_idx] == "3rd"]
test_data$logical_class[female_fp] <- "FP_female_3rd"
# Остальные FP
remaining_fp <- fp_idx[test_data$logical_class[fp_idx] == "Correct"]
test_data$logical_class[remaining_fp] <- "FP_other"

# Классификация ложно-отрицательных (FN)
fn_idx <- which(test_data$error_type == "FN")
# FN: Мужчины младше 20 лет
male_fn <- fn_idx[test_data$sex[fn_idx] == "male" & test_data$age[fn_idx] < 20]
test_data$logical_class[male_fn] <- "FN_male_young"
# FN: Женщины 1-го класса
female_fn <- fn_idx[test_data$sex[fn_idx] == "female" & test_data$pclass[fn_idx] == "1st"]
test_data$logical_class[female_fn] <- "FN_female_1st"
# Остальные FN
remaining_fn <- fn_idx[test_data$logical_class[fn_idx] == "Correct"]
test_data$logical_class[remaining_fn] <- "FN_other"

# Вывод сводной таблицы по логической классификации ошибок
print(table(test_data$logical_class))
