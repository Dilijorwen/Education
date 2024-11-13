from math import sin, sqrt


def f(x):
    return 0.5*x**2 - sin(x)


def dichotomy_method(a, b, eps):
    iter = 0
    delta = eps / 2
    while b - a > eps:
        x1 = (a + b - delta) / 2
        x2 = (a + b + delta) / 2
        if f(x1) < f(x2):
            b = x2
        else:
            a = x1
        iter += 1
    x_min = (a + b) / 2
    return x_min, iter


def golden_method(a, b, eps):
    iter = 0
    phi = (3 - sqrt(5)) / 2
    while b - a > eps:
        x1 = a + (b - a) * phi
        x2 = b - (b - a) * phi
        if f(x1) < f(x2):
            b = x2
        else:
            a = x1
        iter += 1

    x_min = (a + b) / 2
    return x_min, iter


a = 0
b = 1
eps = 0.03

x_min_dichot, iter_dichot = dichotomy_method(a, b, eps)
x_min_gold, iter_gold = golden_method(a, b, eps)

print("Метод дихотомии:")
print(f"Минимум функции достигается в точке x = {x_min_dichot}")
print(f"Функция в минимальной точке: {f(x_min_dichot)}")
print(f"Количество итераций: {iter_dichot}\n")

print("Метод золотого сечения:")
print(f"Минимум функции достигается в точке x = {x_min_gold}")
print(f"Функция в минимальной точке: {f(x_min_gold)}")
print(f"Количество итераций: {iter_gold}")
