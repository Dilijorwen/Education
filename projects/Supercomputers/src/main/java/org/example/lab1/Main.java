package org.example.lab1;

import java.util.*;
import java.util.function.*;

public class Main {
    public static void main(String[] args) {

        Consumer<List<Integer>> printList = list -> {
            System.out.println("Список: " + list);
        };

        Consumer<List<Integer>> printSum = list -> {
            int sum = list.stream().mapToInt(Integer::intValue).sum();
            System.out.println("Сумма: " + sum);
        };

        Consumer<List<Integer>> printEven = list -> {
            list.stream().filter(x -> x % 2 == 0).forEach(x -> System.out.print(x + " "));
            System.out.println();
        };

        FuncActionBool func = action -> {
            List<Integer> nums = Arrays.asList(1, 2, 3, 4, 5);
            action.accept(nums);
            return true;
        };

        System.out.println("printList: " + func.apply(printList));
        System.out.println("printSum: " + func.apply(printSum));
        System.out.println("printEven: " + func.apply(printEven));
    }
}