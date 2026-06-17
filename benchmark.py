"""
Модуль для автоматического тестирования всех алгоритмов.
Генерирует случайные наборы для различных n, запускает алгоритмы,
замеряет время, вычисляет точность, сохраняет результаты в CSV.
"""

import csv
import os
import time
from typing import List, Tuple, Dict, Any
import random

from data_generator import generate_random_items, get_all_tricky_cases
from algorithms import (
    brute_force,
    greedy,
    dynamic_programming,
    simulated_annealing
)

# Список размерностей для тестирования
N_VALUES = [5, 10, 15, 20, 25, 30, 40, 50, 75, 100]
# Количество случайных наборов для каждого n
TRIALS_PER_N = 10
# Вместимость рюкзака будет равна половине суммарного веса (чтобы были интересные случаи)
CAPACITY_RATIO = 0.5


def run_benchmark(
    n_values: List[int] = N_VALUES,
    trials: int = TRIALS_PER_N,
    capacity_ratio: float = CAPACITY_RATIO,
    output_file: str = "results/benchmark_results.csv"
) -> None:
    """
    Запускает бенчмарк для всех алгоритмов.

    Результаты сохраняются в CSV-файл со столбцами:
    n, trial, algorithm, time_seconds, value, accuracy_percent, iterations (для отжига)
    """
    # Создаём папку для результатов, если её нет
    os.makedirs("results", exist_ok=True)

    # Открываем CSV для записи
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'n', 'trial', 'algorithm', 'time_seconds',
            'value', 'accuracy_percent', 'iterations'
        ])

        for n in n_values:
            print(f"Тестирование n = {n} ...")
            for trial in range(trials):
                # Генерируем случайный набор предметов
                # Максимальный вес и стоимость зададим пропорционально n
                max_w = 100 if n <= 30 else 200
                max_v = 100 if n <= 30 else 200
                items = generate_random_items(n, max_weight=max_w, max_value=max_v)

                # Вместимость = capacity_ratio * суммарный вес (чтобы не все предметы влезали)
                total_weight = sum(w for w, _ in items)
                capacity = int(capacity_ratio * total_weight)
                if capacity < 1:
                    capacity = 1

                # Определяем эталон (оптимальное решение)
                # Для n <= 20 используем полный перебор, иначе ДП
                if n <= 20:
                    true_value, _ = brute_force(items, capacity)
                else:
                    true_value, _ = dynamic_programming(items, capacity)

                # Если true_value == 0, все алгоритмы дадут 0, точность неопределена
                # Тогда accuracy будем считать 100% только если алгоритм тоже дал 0

                # Словарь алгоритмов для тестирования
                algorithms_to_test = {
                    "greedy": greedy,
                    "DP": dynamic_programming,
                    "simulated_annealing": lambda it, cap: simulated_annealing(it, cap)
                }
                # Добавляем полный перебор только для n <= 20
                if n <= 20:
                    algorithms_to_test["brute_force"] = brute_force

                # Прогоняем каждый алгоритм
                for algo_name, algo_func in algorithms_to_test.items():
                    start = time.perf_counter()
                    # Вызов алгоритма (возвращает (value, selected) или (value, selected, iter) для отжига)
                    result = algo_func(items, capacity)
                    end = time.perf_counter()
                    elapsed = end - start

                    # Распаковываем результат
                    if algo_name == "simulated_annealing":
                        value, _, iterations = result
                    else:
                        value, _ = result
                        iterations = 0

                    # Вычисляем точность (в % от эталона)
                    if true_value == 0:
                        accuracy = 100.0 if value == 0 else 0.0
                    else:
                        accuracy = (value / true_value) * 100.0

                    # Записываем строку
                    writer.writerow([
                        n, trial, algo_name, elapsed,
                        value, accuracy, iterations
                    ])

            # После каждого n сохраняем данные на диск (принудительно)
            f.flush()


def run_tricky_cases(output_file: str = "results/tricky_results.csv") -> None:
    """
    Тестирует все алгоритмы на специальных провокационных наборах.
    Результаты сохраняются в отдельный CSV.
    """
    os.makedirs("results", exist_ok=True)
    tricky_sets = get_all_tricky_cases()

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'case_id', 'n', 'capacity', 'algorithm',
            'value', 'selected_items', 'time_seconds', 'iterations'
        ])

        for case_id, (items, capacity) in enumerate(tricky_sets, start=1):
            n = len(items)
            print(f"Тестирование провокационного набора #{case_id} (n={n})...")

            # Словарь алгоритмов (включая перебор и ДП для сравнения)
            algos = {
                "brute_force": brute_force,
                "greedy": greedy,
                "DP": dynamic_programming,
                "simulated_annealing": lambda it, cap: simulated_annealing(it, cap)
            }

            for algo_name, algo_func in algos.items():
                start = time.perf_counter()
                result = algo_func(items, capacity)
                end = time.perf_counter()
                elapsed = end - start

                if algo_name == "simulated_annealing":
                    value, selected, iterations = result
                else:
                    value, selected = result
                    iterations = 0

                writer.writerow([
                    case_id, n, capacity, algo_name,
                    value, str(selected), elapsed, iterations
                ])
            f.flush()


if __name__ == "__main__":
    # Запускаем бенчмарк на случайных наборах
    run_benchmark()
    # Запускаем на провокационных наборах
    run_tricky_cases()
    print("Бенчмарк завершён. Результаты сохранены в папке results/")