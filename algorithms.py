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
    # dp[w] — максимальная стоимость для веса w
    dp = [0] * (capacity + 1)
    # Для восстановления запоминаем, брали ли предмет при достижении веса w
    # Используем двумерный массив take[i][w] — брали ли i-й предмет при весе w
    # Но для экономии памяти можно восстановить через отдельный проход.
    # Проще: сохраняем parent[ w ] = (предыдущий вес, индекс предмета)
    # Но для простоты реализуем классический вариант с двумерным массивом, 
    # чтобы восстановление было наглядным.
    # Однако для больших capacity это затратно по памяти. 
    # В учебных целях оставим простой вариант:

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
    T_min: float = 1e-3
) -> Tuple[int, List[int], int]:
    """
    Имитация отжига для приближённого решения задачи 0/1 рюкзака.

    Решение представляется битовым массивом длины n (1 — предмет взят).
    Функция стоимости: суммарная стоимость всех взятых предметов минус штраф за превышение веса.
    Штраф = BIG_M * max(0, total_weight - capacity).

    Параметры:
        items (List[Item]): список предметов
        capacity (int): вместимость
        T0 (float): начальная температура
        alpha (float): коэффициент охлаждения (0 < alpha < 1)
        iterations_per_T (int): число итераций на каждой температуре.
            Если None, то равно 100 * n.
        T_min (float): температура остановки

    Возвращает:
        Tuple[int, List[int], int]: (лучшая стоимость, список индексов, общее число итераций)
    """
    n = len(items)
    if n == 0:
        return 0, [], 0

    if iterations_per_T is None:
        iterations_per_T = 100 * n

    # Штраф за превышение веса (большое число)
    BIG_M = 1000 * max(v for _, v in items) if items else 1000

    # Функция оценки решения (битовый массив)
    def evaluate(solution: List[int]) -> int:
        total_w = 0
        total_v = 0
        for i, bit in enumerate(solution):
            if bit:
                w, v = items[i]
                total_w += w
                total_v += v
        # Если вес превышает вместимость, накладываем штраф
        if total_w > capacity:
            penalty = BIG_M * (total_w - capacity)
            total_v -= penalty
        return total_v

    # Генерация соседнего решения: случайно инвертировать один бит
    def get_neighbor(solution: List[int]) -> List[int]:
        new_sol = solution.copy()
        idx = random.randint(0, n - 1)
        new_sol[idx] = 1 - new_sol[idx]  # инвертируем
        return new_sol

    # Начальное решение — все нули (пустой рюкзак)
    current = [0] * n
    current_value = evaluate(current)

    best = current.copy()
    best_value = current_value

    T = T0
    total_iterations = 0

    while T > T_min:
        for _ in range(iterations_per_T):
            total_iterations += 1
            # Генерируем соседа
            neighbor = get_neighbor(current)
            neighbor_value = evaluate(neighbor)

            delta = neighbor_value - current_value

            # Если сосед лучше или с вероятностью exp(delta/T) принимаем худшего
            if delta > 0 or random.random() < math.exp(delta / T):
                current = neighbor
                current_value = neighbor_value

                # Обновляем лучшее решение
                if current_value > best_value:
                    best = current.copy()
                    best_value = current_value

        # Охлаждение
        T *= alpha

    # Извлекаем индексы выбранных предметов из лучшего решения
    selected = [i for i, bit in enumerate(best) if bit == 1]
    return best_value, selected, total_iterations