package org.example.lab2;

import java.util.*;
import java.util.concurrent.*;

public class Main {

    // Метод, возвращающий подмножество элементов, отличающихся не более чем на 4
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

        System.out.print("Введите размер массива: ");
        int size = scanner.nextInt();

        System.out.print("Введите число для сравнения: ");
        int target = scanner.nextInt();

        // Генерация случайного массива
        Random rand = new Random();
        int[] array = rand.ints(size, 0, 100).toArray();
        System.out.println("Сгенерированный массив: " + Arrays.toString(array));

        // Используем Callable как "делегат" для асинхронного выполнения
        Callable<List<Integer>> task = () -> findSubset(array, target);

        // Используем ExecutorService для асинхронного запуска
        ExecutorService executor = Executors.newSingleThreadExecutor();
        Future<List<Integer>> future = executor.submit(task);

        // Мониторинг выполнения
        while (!future.isDone()) {
            System.out.println("Метод ещё выполняется...");
            Thread.sleep(500); // ожидание 0.5 секунды
        }

        // Получение результата
        List<Integer> subset = future.get();
        System.out.println("Подмножество элементов: " + subset);

        executor.shutdown();
    }
}