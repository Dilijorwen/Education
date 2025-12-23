package org.example.lab7;

import java.util.ArrayList;
import java.util.List;

public class Main {

    public static void main(String[] args) {

        List<ArrayTask> tasks = new ArrayList<>();

        tasks.add(new ArrayTask(15, 10));
        tasks.add(new ArrayTask(20, 25));
        tasks.add(new ArrayTask(18, 7));

        ArrayTaskManager manager =
                new ArrayTaskManager(tasks, 3);

        System.out.println("Starting collection processing...\n");
        manager.processTasks();

        manager.shutdown();
    }
}

