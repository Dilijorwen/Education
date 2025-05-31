setwd("/Users/daniil/Desktop/Обучение/BigData")

DATA_FILE <- "lab2_data.dat"

raw_header   <- readLines(DATA_FILE, n = 1)
clean_header <- gsub("\\s*\\([^()]*\\)", "", raw_header)
clean_header <- gsub("\\s+", " ", clean_header)
clean_header <- trimws(clean_header)


header_tokens <- strsplit(clean_header, " ")[[1]]
col_names_raw <- header_tokens[-1]
col_names_raw <- col_names_raw[-2]
col_names_raw
length(col_names_raw)

make_snake <- function(x) {
  x <- tolower(gsub("[^A-Za-z0-9]+", "_", x))
  # ensure uniqueness (append _n where needed)
  dup <- duplicated(x)
  if (any(dup)) x[dup] <- paste0(x[dup], "_", seq_along(which(dup)))
  x
}
col_names <- make_snake(col_names_raw)
length(col_names)


df <- read.table(
  DATA_FILE,
  header           = FALSE,
  sep              = "",
  stringsAsFactors = FALSE,
  skip             = 1,
  comment.char     = "",
  fill             = TRUE
)

head(df)
df <- df[, -c(1:2)]
df <- df[, -2]
head(df)
dim(df)


names(df) <- col_names
head(df)


factor_cols <- c(
  "gender", "greek", "home_town", "in_state", "ethnicity", "religion",
  "calculus", "cell_phone", "president", "political_party", "section"
)


factor_cols <- intersect(factor_cols, names(df))

df[factor_cols] <- lapply(df[factor_cols], factor)

numeric_mask <- sapply(df, is.numeric)
problem_mat  <- df[, numeric_mask, drop = FALSE] < 0 | df[, numeric_mask, drop = FALSE] == 999
rows_bad     <- rowSums(problem_mat, na.rm = TRUE) > 0

df <- df[!rows_bad, ]

cat("\n\n--- Проверка уровней факторов ---\n")
print(lapply(df[factor_cols], levels))

cat("\n--- Кол-во пропущенных значений ---\n")
print(colSums(is.na(df)))


df$home_bc <- factor(ifelse(df$home_town == "3", 1, 0),
                     levels = c(0, 1),
                     labels = c("other", "big_city"))
head(df)
df_work <- df[, -c(2:11)]
head(df_work)
df_work <- df_work[, -c(4:22)]
head(df_work)
# --------------------------------------------------------------------
# 2. Модели ------------------------------------------------------------
m1 <- lm(drinks_per_week ~ party_hours_per_week + gender, data = df_work)
summary(m1)
m2 <- lm(drinks_per_week ~ party_hours_per_week + gender + home_bc, data = df_work)
summary(m2)

# --------------------------------------------------------------------
# 3. Подготовка предсказаний ------------------------------------------
# Шаг по оси X
xseq <- seq(min(df_work$party_hours_per_week, na.rm = TRUE),
            max(df_work$party_hours_per_week, na.rm = TRUE), length.out = 120)

# --- Пакеты цветов ----------------------------------------------------
col_gender <- c("blue", "red")                           # male, female
names(col_gender) <- levels(df_work$gender)[1:2]

col_combo <- c("darkgreen", "purple", "orange", "brown")   # 4 сочетания
combo_labels <- NULL

# m1: линия, доверительный и предиктивный интервалы для каждого гендера
plot(df_work$party_hours_per_week, df_work$drinks_per_week,
     xlab = "Party hours per week", ylab = "Drinks per week",
     main = "Model m1: by gender", pch = 19, cex = 0.6, col = gray(0.7))

g1 <- levels(df_work$gender)[1]
g2 <- levels(df_work$gender)[2]

# Gender 1
nd1 <- data.frame(party_hours_per_week = xseq,
                  gender = factor(rep(g1, length(xseq)), levels = levels(df_work$gender)))
pred_ci1 <- predict(m1, newdata = nd1, interval = "confidence")
pred_pi1 <- predict(m1, newdata = nd1, interval = "prediction")
base_col1 <- col_gender[g1]
ci_col1   <- adjustcolor(base_col1, alpha.f = 0.25)
pi_col1   <- adjustcolor(base_col1, alpha.f = 0.10)

polygon(c(xseq, rev(xseq)), c(pred_pi1[, "lwr"], rev(pred_pi1[, "upr"])), col = pi_col1, border = NA)
polygon(c(xseq, rev(xseq)), c(pred_ci1[, "lwr"], rev(pred_ci1[, "upr"])), col = ci_col1, border = NA)
lines(xseq, pred_ci1[, "fit"], col = base_col1, lwd = 2)

# Gender 2
nd2 <- data.frame(party_hours_per_week = xseq,
                  gender = factor(rep(g2, length(xseq)), levels = levels(df_work$gender)))
pred_ci2 <- predict(m1, newdata = nd2, interval = "confidence")
pred_pi2 <- predict(m1, newdata = nd2, interval = "prediction")
base_col2 <- col_gender[g2]
ci_col2   <- adjustcolor(base_col2, alpha.f = 0.25)
pi_col2   <- adjustcolor(base_col2, alpha.f = 0.10)

polygon(c(xseq, rev(xseq)), c(pred_pi2[, "lwr"], rev(pred_pi2[, "upr"])), col = pi_col2, border = NA)
polygon(c(xseq, rev(xseq)), c(pred_ci2[, "lwr"], rev(pred_ci2[, "upr"])), col = ci_col2, border = NA)
lines(xseq, pred_ci2[, "fit"], col = base_col2, lwd = 2)

legend("topleft", legend = paste("Gender =", c(g1, g2)), lwd = 2, col = c(base_col1, base_col2), bty = "n")

# 5. График m2 (без циклов, только линии для каждого сочетания) ----------

plot(df_work$party_hours_per_week, df_work$drinks_per_week,
     xlab = "Party hours per week", ylab = "Drinks per week",
     main = "Model m2: gender × home", pch = 19, cex = 0.6, col = gray(0.7))

# G1 + H1
h1 <- levels(df_work$home_bc)[1]
h2 <- levels(df_work$home_bc)[2]
combo_cols <- c("darkgreen", "purple", "orange", "brown")

nd11 <- data.frame(party_hours_per_week = xseq,
                   gender = factor(rep(g1, length(xseq)), levels = levels(df_work$gender)),
                   home_bc = factor(rep(h1, length(xseq)), levels = levels(df_work$home_bc)))
lines(xseq, predict(m2, newdata = nd11), col = combo_cols[1], lwd = 2)

# G1 + H2
nd12 <- nd11
nd12$home_bc <- factor(rep(h2, length(xseq)), levels = levels(df_work$home_bc))
lines(xseq, predict(m2, newdata = nd12), col = combo_cols[2], lwd = 2)

# G2 + H1
nd21 <- nd11
nd21$gender <- factor(rep(g2, length(xseq)), levels = levels(df_work$gender))
nd21$home_bc <- factor(rep(h1, length(xseq)), levels = levels(df_work$home_bc))
lines(xseq, predict(m2, newdata = nd21), col = combo_cols[3], lwd = 2)

# G2 + H2
nd22 <- nd21
nd22$home_bc <- factor(rep(h2, length(xseq)), levels = levels(df_work$home_bc))
lines(xseq, predict(m2, newdata = nd22), col = combo_cols[4], lwd = 2)

legend("topleft",
       legend = c(
         paste("G", g1, "/ H", h1, sep = ""),
         paste("G", g1, "/ H", h2, sep = ""),
         paste("G", g2, "/ H", h1, sep = ""),
         paste("G", g2, "/ H", h2, sep = "")
       ),
       lwd = 2, col = combo_cols, bty = "n")