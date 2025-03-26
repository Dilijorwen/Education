import numpy as np
import matplotlib.pyplot as plt

class HeaterInCup:
    def __init__(self, power, heater_mass, heater_capacity, water_volume,
                 initial_temp, heat_transfer_coeff, radiation_coeff, surface_area,
                 water_density, water_capacity, vaporization_heat, ambient_temp):
        """
        Инициализация параметров модели:
        power               - мощность нагревателя (Вт)
        heater_mass         - масса нагревателя (кг)
        heater_capacity     - удельная теплоёмкость нагревателя (Дж/(кг·K))
        water_volume        - объём воды (м³)
        initial_temp        - начальная температура системы (K)
        heat_transfer_coeff - коэффициент конвективных потерь (Вт/(м²·K))
        radiation_coeff     - коэффициент излучения (Вт/(м²·K⁴)); например, для абсолютно черного тела – постоянная Стефана–Больцмана
        surface_area        - площадь поверхности нагревателя (м²)
        water_density       - плотность воды (кг/м³)
        water_capacity      - удельная теплоёмкость воды (Дж/(кг·K))
        vaporization_heat   - удельная теплота парообразования воды (Дж/кг)
        ambient_temp        - температура окружающей среды (K)
        """
        self.power = power
        self.m_heater = heater_mass
        self.c_heater = heater_capacity
        self.V = water_volume
        self.T = initial_temp
        self.alpha = heat_transfer_coeff
        self.k = radiation_coeff
        self.S = surface_area
        self.rho_water = water_density
        self.c_water = water_capacity
        self.Lv = vaporization_heat
        self.T_ambient = ambient_temp
        self.T_burn = 773                     # Температура сгорания нагревателя (500°C)
        self.T_boiling = 373                  # Температура кипения воды (100°C)

    def total_heat_capacity(self):
        """ Рассчитываем суммарную теплоёмкость системы """
        if self.V > 0:
            m_water = self.V * self.rho_water
            return m_water * self.c_water + self.m_heater * self.c_heater
        else:
            return self.m_heater * self.c_heater

    def heat_loss(self):
        """
        Тепловые потери:
          - Конвективные: alpha * S * (T - T_ambient)
          - Излучательные: k * S * (T^4 - T_ambient^4)
        """
        conv_loss = self.alpha * self.S * (self.T - self.T_ambient)
        rad_loss = self.k * self.S * (self.T**4 - self.T_ambient**4)
        return conv_loss + rad_loss

    def dVdt(self):
        if self.V > 0 and self.T >= self.T_boiling:
            net_power = self.power - self.heat_loss()
            # Если нет свободной энергии, испарения не происходит
            if net_power > 0:
                return - net_power / (self.rho_water * self.Lv)
            else:
                return 0
        return 0

    def dTdt(self):
        """
        Скорость изменения температуры:
          Если вода кипит (T >= T_boiling) и она присутствует, температура остается постоянной (энергия уходит на испарение)
          Иначе: dT/dt = (P - heat_loss) / (total_heat_capacity)
        """
        if self.V > 0 and self.T >= self.T_boiling:
            return 0
        else:
            return (self.power - self.heat_loss()) / self.total_heat_capacity()

    def step(self, dt):
        """ Один шаг моделирования: обновляем температуру и объём воды """
        self.T += self.dTdt() * dt
        self.V += self.dVdt() * dt
        if self.V < 0:
            self.V = 0

    def is_burned(self):
        """ Проверка: если температура достигает или превышает температуру сгорания, модель сигнализирует об этом """
        return self.T >= self.T_burn

def simulate_heater(power, heater_mass, heater_capacity, water_volume,
                    initial_temp, heat_transfer_coeff, radiation_coeff, surface_area,
                    water_density, water_capacity, vaporization_heat, ambient_temp,
                    dt=1, t_max=300600):
    """
    Функция симуляции:
      - dt: шаг по времени (сек)
      - t_max: максимальное время симуляции (сек)
    Возвращает временной ряд, температуру и объём воды.
    """
    heater = HeaterInCup(power, heater_mass, heater_capacity, water_volume,
                         initial_temp, heat_transfer_coeff, radiation_coeff, surface_area,
                         water_density, water_capacity, vaporization_heat, ambient_temp)
    times = [0]
    temps = [initial_temp]
    volumes = [water_volume]

    for t in range(1, t_max+1):
        heater.step(dt)
        times.append(t)
        temps.append(heater.T)
        volumes.append(heater.V)
        if heater.is_burned():
            print(f"Нагреватель сгорел на {t} сек при {heater.T - 273.15:.1f} °C")
            break
    return times, temps, volumes

# Параметры системы
power = 500                   # Мощность (Вт)
heater_mass = 0.1              # Масса нагревателя (кг)
heater_capacity = 500          # Теплоёмкость нагревателя (Дж/(кг·K))
water_volume = 0.7 / 1000      # Объём воды 500 мл (перевод в м³)
initial_temp = 298             # Начальная температура 25°C (в Кельвинах)
heat_transfer_coeff = 10       # Коэффициент конвекции (Вт/(м²·K))
radiation_coeff = 5.67e-8      # Коэффициент излучения (Постоянная Стефана-Больцмана для идеального черного тела)
surface_area = 0.01            # Площадь поверхности нагревателя (м²)
water_density = 1000           # Плотность воды (кг/м³)
water_capacity = 4180          # Теплоёмкость воды (Дж/(кг·K))
vaporization_heat = 2.26e6     # Удельная теплота парообразования воды (Дж/кг)
ambient_temp = 298             # Температура окружающей среды (25°C в K)

# Запуск симуляции
times, temps, volumes = simulate_heater(power, heater_mass, heater_capacity, water_volume,
                                        initial_temp, heat_transfer_coeff, radiation_coeff, surface_area,
                                        water_density, water_capacity, vaporization_heat, ambient_temp,
                                        dt=1, t_max=30060)

# Визуализация результатов
plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
plt.plot(times, np.array(temps) - 273.15, label="Температура")
plt.axhline(100, color='orange', linestyle='--', label="Кипение (100°C)")
plt.axhline(500, color='red', linestyle='--', label="Сгорание (500°C)")
plt.xlabel("Время (с)")
plt.ylabel("Температура (°C)")
plt.legend()
plt.grid()

plt.subplot(1, 2, 2)
plt.plot(times, np.array(volumes) * 1000, label="Объём воды")
plt.xlabel("Время (с)")
plt.ylabel("Объём воды (мл)")
plt.legend()
plt.grid()

plt.suptitle("Модель нагревателя в кружке с учетом конвекции и излучения")
plt.show()



