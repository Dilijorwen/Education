# temp_serial_logger

Кроссплатформенная программа на C++ (Windows/Linux/macOS), которая:
1) считывает температуру из устройства по Serial/USB (COM/tty) или из `stdin`,
2) пишет все измерения в лог, храня только последние 24 часа,
3) считает среднюю температуру за каждый час и хранит только последние 30 суток,
4) считает среднюю температуру за каждый день и накапливает данные за текущий год.

Агрегация выполняется по UTC (границы часа/суток считаются по UTC).

---

## Сборка

### Linux/macOS

```bash
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

### Windows

```PowerShell
cmake -S . -B build -G Ninja -DCMAKE_CXX_COMPILER=g++
cmake --build build
```


## Запуск

### Linux

```bash
cd /path/to/temp_serial_logger/build
./temp_simulator --period-ms 1000 --base 23 --amp 2 --noise 0.2 | ./temp_logger --stdin
```
### Windows

```PowerShell
cd C:\path\to\temp_serial_logger\build
cmd /c ".\temp_simulator.exe --period-ms 1000 --base 23 --amp 2 --noise 0.2 | .\temp_logger.exe --stdin"
```