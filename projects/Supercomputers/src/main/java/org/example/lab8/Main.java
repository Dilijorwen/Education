package org.example.lab8;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.concurrent.FutureTask;

public class Main {

    public static void main(String[] args) throws Exception {

        int rows = 4;
        int cols = 6;

        int[][] matrix = new int[rows][cols];
        Random random = new Random();

        System.out.println("Generated matrix:");
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                matrix[i][j] = random.nextInt(50);
                System.out.print(matrix[i][j] + "\t");
            }
            System.out.println();
        }

        List<FutureTask<Integer>> tasks = new ArrayList<>();
        List<Thread> threads = new ArrayList<>();

        for (int i = 0; i < rows; i++) {
            FutureTask<Integer> task =
                    new FutureTask<>(new EvenCountTask(matrix[i]));

            Thread thread = new Thread(task);

            tasks.add(task);
            threads.add(thread);

            thread.start();
        }

        int totalEvenCount = 0;
        for (FutureTask<Integer> task : tasks) {
            totalEvenCount += task.get();
        }

        System.out.println(
                "\nNumber of even elements in the matrix: "
                        + totalEvenCount
        );
    }
}