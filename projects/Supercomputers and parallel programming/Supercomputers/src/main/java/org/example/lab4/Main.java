package org.example.lab4;

import java.util.Random;
import java.util.Scanner;
import java.util.concurrent.*;
import java.util.function.Consumer;

public class Main {

    public static double calculateAverage(int rows, int cols) {
        Random random = new Random();
        int[][] matrix = new int[rows][cols];

        double sum = 0.0;

        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                matrix[i][j] = random.nextInt(100);
                sum += matrix[i][j];
            }
        }

        System.out.println("Generated matrix:");
        for (int[] row : matrix) {
            System.out.println(java.util.Arrays.toString(row));
        }

        return sum / (rows * cols);
    }

    public static void calculateAverageAsync(
            int rows,
            int cols,
            Consumer<Double> callback
    ) {
        ExecutorService executor = Executors.newSingleThreadExecutor();

        Callable<Double> task = () -> calculateAverage(rows, cols);

        Future<Double> future = executor.submit(task);

        new Thread(() -> {
            try {
                Double result = future.get();
                callback.accept(result);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }).start();

        executor.shutdown();
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);


        System.out.print("Enter the number of rows: ");
        int rows = scanner.nextInt();

        System.out.print("Enter the number of cols: ");
        int cols = scanner.nextInt();

        System.out.println("Asynchronous start of averaging calculation...");

        calculateAverageAsync(rows, cols, average ->
                System.out.println(
                        "Callback: arithmetic mean = " + average
                )
        );

        System.out.println("The main thread continues execution.");
    }
}