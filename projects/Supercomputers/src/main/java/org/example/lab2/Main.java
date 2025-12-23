package org.example.lab2;

import java.util.*;
import java.util.concurrent.*;

public class Main {

    public static List<Integer> findSubset(int[] array, int target) {
        List<Integer> result = new ArrayList<>();
        for (int num : array) {
            if (Math.abs(num - target) <= 4) {
                result.add(num);
            }
        }
        return result;
    }

    public static void main(String[] args) throws InterruptedException, ExecutionException {
        Scanner scanner = new Scanner(System.in);

        System.out.print("Enter the array size: ");
        int size = scanner.nextInt();

        System.out.print("Enter the number to compare: ");
        int target = scanner.nextInt();

        Random rand = new Random();
        int[] array = rand.ints(size, 0, 100).toArray();
        System.out.println("Generated array: " + Arrays.toString(array));

        Callable<List<Integer>> task = () -> findSubset(array, target);

        ExecutorService executor = Executors.newSingleThreadExecutor();
        Future<List<Integer>> future = executor.submit(task);


        List<Integer> subset = future.get();
        System.out.println("Subset of elements: " + subset);

        executor.shutdown();
    }
}