#include "stdio.h"

#define CUDA_CHECK_ERROR(err)           \
if ((err) != cudaSuccess) {          \
    printf("Cuda error: %s\n", cudaGetErrorString(err));    \
    printf("Error in file: %s, line: %i\n", __FILE__, __LINE__);  \
}

__global__ void add_kernel(int* a, int* b, int* c){
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    c[i] = a[i] + b[i];
}

//void add(int* a, int* b, int* c, int n){
//    for(int i = 0; i < n; i++){
//        c[i] = a[i] + b[i];
//    }
//}

int main(){

    int n = 1 << 30;
    //host mem

    auto a = new int [n];
    auto b = new int [n];
    auto c = new int [n];

    for(int i = 0; i < n; i++){
        a[i] = i;
        b[i] = i;
        c[i] = 0;
    }
    //dev mem

    int *a_dev, *b_dev, *c_dev;

    CUDA_CHECK_ERROR(cudaMalloc(&a_dev, n * sizeof(int)))
    CUDA_CHECK_ERROR(cudaMalloc(&b_dev, n * sizeof(int)))
    CUDA_CHECK_ERROR(cudaMalloc(&c_dev, n * sizeof(int)))

    //host to dev memcpy

    //cudaMemCpy(dst, src, count, type)
    CUDA_CHECK_ERROR(cudaMemcpy(a_dev, a, n * sizeof(int), cudaMemcpyHostToDevice))
    CUDA_CHECK_ERROR(cudaMemcpy(b_dev, b, n * sizeof(int), cudaMemcpyHostToDevice))
    CUDA_CHECK_ERROR(cudaMemcpy(c_dev, c, n * sizeof(int), cudaMemcpyHostToDevice))

    //kernel
    int threads = 1024;
    int block = (n + threads - 1) / threads;
    add_kernel <<<block, threads>>> (a_dev, b_dev, c_dev);


    //dev to host memcpy
    CUDA_CHECK_ERROR(cudaMemcpy(c, c_dev, n * sizeof(int), cudaMemcpyDeviceToHost))

    //print ans
    for(int i = 1 << 10; i < ((1 << 10) + 100); i++){
        printf("c[%i] = %i\n", i, c[i]);
    }
}