package org.example.lab6;

import java.util.Random;

public class Main {

    public static void main(String[] args) throws InterruptedException {

        int arraySize = 30;
        int target = 7;

        int[] array = new int[arraySize];
        Random random = new Random();

        System.out.println("Initial array:");
        for (int i = 0; i < arraySize; i++) {
            array[i] = random.nextInt(10);
            System.out.print(array[i] + " ");
        }
        System.out.println("\n");

        int threadCount = 3;
        SearchThread[] threads = new SearchThread[threadCount];

        int chunkSize = arraySize / threadCount;

        for (int i = 0; i < threadCount; i++) {
            int start = i * chunkSize;
            int end = (i == threadCount - 1)
                    ? arraySize
                    : start + chunkSize;

            threads[i] = new SearchThread(
                    array,
                    start,
                    end,
                    target,
                    "Thread-" + i
            );
        }

        System.out.println("Starting threads...\n");
        for (SearchThread thread : threads) {
            thread.start();
        }

        boolean exists = false;
        for (SearchThread thread : threads) {
            thread.join();
            if (thread.isFound()) {
                exists = true;
            }
        }

        System.out.println(
                "\nFinal result: element " +
                        target +
                        (exists ? " found in the array." : " not found in the array.")
        );
    }
}
