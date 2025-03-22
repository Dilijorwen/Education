#include <stdio.h>

__global__ void hw(){
    int index_x = blockIdx.x * blockDim.x + threadIdx.x;
    int index_y = blockIdx.y * blockDim.y + threadIdx.y;
    int index_z = blockIdx.z * blockDim.z + threadIdx.z;

    int index = index_x + index_y * gridDim.x * blockDim.x + index_z * gridDim.y * blockDim.y * gridDim.x * blockDim.x;

    printf("Hello World! From (%d, %d, %d) with inx %d\n", index_x, index_y, index_z, index);
}

int main(){
    dim3 blocks(1,1,1);
    dim3 threads(4,4,4);

    hw <<<blocks, threads>>>();

    cudaDeviceSynchronize();

}