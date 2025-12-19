package org.example.lab5;

public class SumThread extends Thread {

    private int[] array;
    private int start;
    private int end;
    private int partialSum;

    public SumThread(int[] array, int start, int end, String name) {
        super(name);
        this.array = array;
        this.start = start;
        this.end = end;
    }

    @Override
    public void run() {
        System.out.println(
                "Thread" + getName() +
                        " began work. Range: [" + start + ", " + end + ")"
        );

        partialSum = 0;
        for (int i = start; i < end; i++) {
            partialSum += array[i];

            System.out.println(
                    "Thread " + getName() +
                            " processes an element " + i +
                            ", current value of the sum = " + partialSum
            );

            try {
                Thread.sleep(100); // имитация нагрузки
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }

        System.out.println(
                "Thread " + getName() +
                        " completed the work. Partial amount = " + partialSum
        );
    }

    public int getPartialSum() {
        return partialSum;
    }
}

