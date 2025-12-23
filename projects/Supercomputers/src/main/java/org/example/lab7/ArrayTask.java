package org.example.lab7;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class ArrayTask {

    private int[] array;
    private int target;

    public ArrayTask(int size, int target) {
        this.target = target;
        this.array = new int[size];

        Random random = new Random();
        for (int i = 0; i < size; i++) {
            array[i] = random.nextInt(50);
        }
    }

    public List<Integer> findSubset() throws InterruptedException {
        List<Integer> result = new ArrayList<>();

        for (int value : array) {
            Thread.sleep(50);

            if (Math.abs(value - target) <= 4) {
                result.add(value);
            }
        }

        return result;
    }

    public int[] getArray() {
        return array;
    }

    public int getTarget() {
        return target;
    }
}

