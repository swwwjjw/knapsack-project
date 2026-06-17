"""
Модуль содержит реализацию четырёх алгоритмов для задачи о рюкзаке 0/1:
- полный перебор (только для малых n)
- жадный алгоритм
- динамическое программирование (точное)
- имитация отжига (приближённый)
"""

import random
import math
import time
from typing import List, Tuple, Set

# Тип данных: предмет (вес, стоимость)
Item = Tuple[int, int]


# ------------------- Полный перебор -------------------
def brute_force(items: List[Item], capacity: int) -> Tuple[int, List[int]]:
    """
    Полный перебор всех подмножеств (2^n). Применяется только для n <= 20.

    Параметры:
        items (List[Item]): список предметов (вес, стоимость)
        capacity (int): вместимость рюкзака

    Возвращает:
        Tuple[int, List[int]]: (максимальная стоимость, список индексов выбранных предметов)
    """
    n = len(items)
    best_value = 0
    best_mask = 0

    # Перебираем все битовые маски от 0 до 2^n - 1
    for mask in range(1 << n):
        total_weight = 0
        total_value = 0
        # Проверяем каждый бит
        for i in range(n):
            if mask & (1 << i):
                w, v = items[i]
                total_weight += w
                total_value += v
                # Если вес превысил вместимость, прерываем (этот набор недопустим)
                if total_weight > capacity:
                    break
        # Если допустим и лучше текущего лучшего, запоминаем
        if total_weight <= capacity and total_value > best_value:
            best_value = total_value
            best_mask = mask

    # Формируем список индексов выбранных предметов
    selected = [i for i in range(n) if best_mask & (1 << i)]
    return best_value, selected


# ------------------- Жадный алгоритм -------------------
def greedy(items: List[Item], capacity: int) -> Tuple[int, List[int]]:
    """
    Жадный алгоритм: сортировка по убыванию удельной стоимости (ценность/вес).
    Затем последовательное добавление предметов, пока они помещаются.

    Возвращает:
        Tuple[int, List[int]]: (итоговая стоимость, список индексов)
    """
    n = len(items)
    # Создаём список индексов и сортируем по убыванию отношения value/weight
    indices = list(range(n))
    indices.sort(key=lambda i: items[i][1] / items[i][0], reverse=True)

    total_weight = 0
    total_value = 0
    selected = []

    for i in indices:
        w, v = items[i]
        if total_weight + w <= capacity:
            total_weight += w
            total_value += v
            selected.append(i)

    return total_value, selected


# ------------------- Динамическое программирование -------------------
def dynamic_programming(items: List[Item], capacity: int) -> Tuple[int, List[int]]:
    """
    Динамическое программирование для задачи 0/1 рюкзака.
    Используется одномерный массив dp[w] = максимальная стоимость при весе w.
    Восстановление выбранных предметов производится обратным проходом.

    Возвращает:
        Tuple[int, List[int]]: (максимальная стоимость, список индексов)
    """
    n = len(items)

    # Создаём таблицу dp как список списков (n+1) x (capacity+1) для восстановления
    dp_table = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        w_i, v_i = items[i - 1]
        for w in range(capacity + 1):
            if w_i <= w:
                # Если берём предмет i-1 (индексация в списке)
                take = dp_table[i - 1][w - w_i] + v_i
                not_take = dp_table[i - 1][w]
                dp_table[i][w] = max(take, not_take)
            else:
                dp_table[i][w] = dp_table[i - 1][w]

    best_value = dp_table[n][capacity]

    # Восстановление выбранных предметов
    selected = []
    w = capacity
    for i in range(n, 0, -1):
        if dp_table[i][w] != dp_table[i - 1][w]:
            # Значит, предмет i-1 был взят
            selected.append(i - 1)
            w -= items[i - 1][0]

    selected.reverse()  # Индексы в порядке возрастания
    return best_value, selected


# ------------------- Имитация отжига -------------------
def simulated_annealing(
    items: List[Item],
    capacity: int,
    T0: float = 1000.0,
    alpha: float = 0.98,
    iterations_per_T: int = None,
    T_min: float = 1e-3,
    random_seed: int = None
) -> Tuple[int, List[int], int]:
    """
    Имитация отжига для приближённого решения задачи 0/1 рюкзака с гарантией допустимости.

    Возвращает:
        Tuple[int, List[int], int]: (фактическая стоимость, список индексов, число итераций)
    """
    if random_seed is not None:
        random.seed(random_seed)

    n = len(items)
    if n == 0:
        return 0, [], 0

    if iterations_per_T is None:
        iterations_per_T = 100 * n

    # Штраф за превышение веса – достаточно большая константа
    total_value_all = sum(v for _, v in items)
    BIG_M = total_value_all + 1 if total_value_all > 0 else 1000

    # Оценочная функция со штрафом
    def evaluate(solution: List[int]) -> int:
        total_w = 0
        total_v = 0
        for i, bit in enumerate(solution):
            if bit:
                w, v = items[i]
                total_w += w
                total_v += v
        if total_w > capacity:
            total_v -= BIG_M * (total_w - capacity)
        return total_v

    # Генерация соседа – инвертирование одного случайного бита
    def get_neighbor(solution: List[int]) -> List[int]:
        new_sol = solution.copy()
        idx = random.randint(0, n - 1)
        new_sol[idx] = 1 - new_sol[idx]
        return new_sol

    # Начальное решение – пустой рюкзак (всегда допустимо)
    current = [0] * n
    current_value = evaluate(current)
    best = current.copy()
    best_value = current_value

    T = T0
    total_iterations = 0

    while T > T_min:
        for _ in range(iterations_per_T):
            total_iterations += 1
            neighbor = get_neighbor(current)
            neighbor_value = evaluate(neighbor)
            delta = neighbor_value - current_value

            if delta > 0 or random.random() < math.exp(delta / T):
                current = neighbor
                current_value = neighbor_value
                if current_value > best_value:
                    best = current.copy()
                    best_value = current_value
        T *= alpha

    # Извлекаем индексы из лучшего (по штрафованной оценке) решения
    selected = [i for i, bit in enumerate(best) if bit == 1]

    # ---- Постобработка: приводим вес к допустимому ----
    total_w = sum(items[i][0] for i in selected)
    # Удаляем предметы с наихудшей удельной ценностью, пока вес не станет ≤ capacity
    while total_w > capacity and selected:
        # Выбираем только предметы с положительным весом (иначе вес не уменьшится)
        candidates = [i for i in selected if items[i][0] > 0]
        if not candidates:
            break  # остались только предметы с нулевым весом – вес уже не уменьшить
        # Удаляем предмет с минимальным отношением ценности к весу
        idx_to_remove = min(candidates, key=lambda i: items[i][1] / items[i][0])
        selected.remove(idx_to_remove)
        total_w -= items[idx_to_remove][0]

    # Фактическая стоимость (без штрафа) допустимого набора
    actual_value = sum(items[i][1] for i in selected)

    return actual_value, selected, total_iterations