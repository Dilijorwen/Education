package org.example.lab5;

import java.util.Random;

public class Main {

    public static void main(String[] args) throws InterruptedException {

        int arraySize = 10;
        int threadCount = 4;

        int[] array = new int[arraySize];
        Random random = new Random();

        System.out.println("Initial array:");
        for (int i = 0; i < arraySize; i++) {
            array[i] = random.nextInt(10);
            System.out.print(array[i] + " ");
        }
        System.out.println("\n");

        SumThread[] threads = new SumThread[threadCount];

        int chunkSize = arraySize / threadCount;

        for (int i = 0; i < threadCount; i++) {
            int start = i * chunkSize;
            int end = (i == threadCount - 1)
                    ? arraySize
                    : start + chunkSize;

            threads[i] = new SumThread(
                    array,
                    start,
                    end,
                    "Thread-" + i
            );
        }

        System.out.println("Starting streams...\n");
        for (SumThread thread : threads) {
            thread.start();
        }

        int totalSum = 0;
        for (SumThread thread : threads) {
            thread.join();
            totalSum += thread.getPartialSum();
        }

        System.out.println("\nAll streams have been completed.");
        System.out.println("Total sum of array elements = " + totalSum);
    }
}