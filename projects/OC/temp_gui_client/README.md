# temp_gui_client

GUI-приложение на C++/Qt6 для ранее созданного сервера температуры (`temp_serial_logger_v2`).

Показывает:
1) текущую температуру (HTTP `GET /api/current`),
2) статистику за выбранный период (min/max/avg/count) (HTTP `GET /api/stats`),
3) график температуры за выбранный период (HTTP `GET /api/series`).

GUI не хранит данные локально — только читает HTTP API сервера.

---

## Требования

- Запущенный сервер `temp_serial_logger_v2` с параметром `--http` (например, 8080).
- CMake >= 3.16
- Компилятор C++17
- Qt6 компоненты: **Widgets**, **Network**, **Charts**
- Ninja (желательно)

---

## Сборка

### Linux/macOS

```bash
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build build

```

### Windows

```PowerShell
cmake -S . -B build -G Ninja
cmake --build build
```


## Запуск

### Linux

```bash
cd build
./temp_gui_client
```
### Windows

```PowerShell
cd build
.\temp_gui_client.exe
```

