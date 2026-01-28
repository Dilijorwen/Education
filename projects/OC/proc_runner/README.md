# hello_world

## Сборка

### Linux/macOS

```bash
mkdir -p build
cmake -S . -B build
cmake --build build -j
```

### Windows

```PowerShell
cmake -S . -B build
cmake --build build -j
```


## Запуск

### Windows

```bash
build\proc_test.exe cmd /c "exit /b 7"
```

### Linux/macOS

```bash
./build/proc_test /bin/sh -c "exit 7"
```