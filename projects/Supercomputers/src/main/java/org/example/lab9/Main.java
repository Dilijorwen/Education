package org.example.lab9;

import java.util.Arrays;
import java.util.Random;
import java.util.Scanner;
import java.util.concurrent.CompletableFuture;

public class Main {

    public static void main(String[] args) {

        Scanner scanner = new Scanner(System.in);

        System.out.print("Enter the size of the array: ");
        int size = scanner.nextInt();

        System.out.print("Enter a number for comparison: ");
        int target = scanner.nextInt();

        CompletableFuture<int[]> generateArrayTask =
                CompletableFuture.supplyAsync(() -> {
                    int[] array = new int[size];
                    Random random = new Random();

                    for (int i = 0; i < size; i++) {
                        array[i] = random.nextInt(50);
                    }

                    System.out.println(
                            "Generated array: " +
                                    Arrays.toString(array)
                    );

                    return array;
                });

        CompletableFuture<Void> maxEvenTask =
                generateArrayTask.thenAcceptAsync(array -> {
                    Integer maxEven = null;

                    for (int value : array) {
                        if (value % 2 == 0) {
                            if (maxEven == null || value > maxEven) {
                                maxEven = value;
                            }
                        }
                    }

                    System.out.println(
                            "Maximum even element: " +
                                    (maxEven != null ? maxEven : "not found")
                    );
                });

        CompletableFuture<Void> countCloseTask =
                generateArrayTask.thenAcceptAsync(array -> {
                    int count = 0;

                    for (int value : array) {
                        if (Math.abs(value - target) <= 3) {
                            count++;
                        }
                    }

                    System.out.println(
                            "Number of elements differing from " +
                                    target + " no more than 3: " + count
                    );
                });

        CompletableFuture.allOf(maxEvenTask, countCloseTask).join();
    }
}

