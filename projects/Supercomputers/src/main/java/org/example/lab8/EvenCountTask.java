package org.example.lab8;

import java.util.concurrent.Callable;

public class EvenCountTask implements Callable<Integer> {

    private int[] row;

    public EvenCountTask(int[] row) {
        this.row = row;
    }

    @Override
    public Integer call() {
        int count = 0;
        for (int value : row) {
            if (value % 2 == 0) {
                count++;
            }
        }
        return count;
    }
}

