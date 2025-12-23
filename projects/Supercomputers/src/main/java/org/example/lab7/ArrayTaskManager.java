package org.example.lab7;

import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class ArrayTaskManager {

    private List<ArrayTask> tasks;
    private ExecutorService executor;

    public ArrayTaskManager(List<ArrayTask> tasks, int poolSize) {
        this.tasks = tasks;
        this.executor = Executors.newFixedThreadPool(poolSize);
    }

    public void processTasks() {
        for (ArrayTask task : tasks) {
            executor.submit(() -> {
                try {
                    System.out.println(
                            Thread.currentThread().getName() +
                                    " started processing. Desired number = " + task.getTarget()
                    );

                    List<Integer> subset = task.findSubset();

                    System.out.println(
                            Thread.currentThread().getName() +
                                    " completed processing. Result = " + subset
                    );

                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            });
        }
    }

    public void shutdown() {
        executor.shutdown();
    }
}

