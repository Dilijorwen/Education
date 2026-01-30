# temp_serial_logger

Расширение проекта из предыдущего задания:
- чтение температуры из Serial/USB (COM/tty) **или** из `stdin` (для симулятора);
- хранение данных **в SQLite** вместо файлов;
- HTTP-сервер, который публикует:
    - текущую температуру,
    - статистику за период,
    - временной ряд для графика;
- клиентское веб-приложение (HTML/JS), отображающее таблицу и график.

Агрегации и “retention” выполняются по UTC.
---

## Зависимости

### Single-header библиотеки (лежат в репозитории)
- `third_party/httplib.h` — cpp-httplib
- `third_party/json.hpp` — nlohmann/json

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
cd build
./temp_simulator --period-ms 1000 --base 23 --amp 2 --noise 0.2 | \
./temp_logger --stdin --http 8080 --web ../web --db ../data/temps.sqlite
```
### Windows

```PowerShell
cd build
cmd /c ".\temp_simulator.exe --period-ms 1000 --base 23 --amp 2 --noise 0.2 | .\temp_logger.exe --stdin --http 8080 --web ..\web --db ..\data\temps.sqlite"
```

```web
http://localhost:8080/
```