package org.example.lab6;

public class SearchThread extends Thread {

    private int[] array;
    private int start;
    private int end;
    private int target;
    private boolean found;

    public SearchThread(int[] array, int start, int end, int target, String name) {
        super(name);
        this.array = array;
        this.start = start;
        this.end = end;
        this.target = target;
        this.found = false;
    }

    @Override
    public void run() {
        System.out.println(
                getName() +
                        " started searching in the range [" + start + ", " + end + ")"
        );

        for (int i = start; i < end; i++) {
            if (array[i] == target) {
                found = true;
                System.out.println(
                        getName() +
                                " found the meaning " + target +
                                " by index " + i
                );
                break;
            }
        }

        System.out.println(
                getName() +
                        " completed the work. Result = " + found
        );
    }

    public boolean isFound() {
        return found;
    }
}
