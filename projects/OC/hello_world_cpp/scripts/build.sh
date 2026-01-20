set -e

BUILD_DIR=build

git pull

mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"
cmake ..
cmake --build .
