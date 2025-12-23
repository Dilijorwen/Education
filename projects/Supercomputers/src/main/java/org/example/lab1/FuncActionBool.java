package org.example.lab1;

import java.util.List;
import java.util.function.Consumer;

@FunctionalInterface
interface FuncActionBool {
    boolean apply(Consumer<List<Integer>> action);
}