package org.example.lab1;

import java.util.List;
import java.util.function.Consumer;

// Собственный функциональный интерфейс, аналог Func<Action<List<Integer>>, Boolean>
@FunctionalInterface
interface FuncActionBool {
    boolean apply(Consumer<List<Integer>> action);
}