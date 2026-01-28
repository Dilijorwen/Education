# cross_prog

## Сборка

### Linux/macOS

```bash
mkdir -p build
cmake -S . -B build
cmake --build build -j
./build/bin/program
```

### Windows

```PowerShell
mkdir build
cmake -S . -B build
cmake --build build --config Release
build\bin\program.exe
```


## Запуск

```bash
get
set 123
get
quit
```