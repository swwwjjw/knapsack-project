"""
Модуль генерации тестовых данных для задачи о рюкзаке.
Генерирует случайные наборы предметов, а также специальные "провокационные" наборы,
на которых жадный алгоритм даёт неоптимальное решение.
"""

import random
from typing import List, Tuple

# Тип данных: предмет описывается кортежем (вес, стоимость)
Item = Tuple[int, int]


def generate_random_items(n: int, max_weight: int = 100, max_value: int = 100) -> List[Item]:
    """
    Генерирует n случайных предметов.

    Параметры:
        n (int): количество предметов
        max_weight (int): максимальный вес предмета
        max_value (int): максимальная стоимость предмета

    Возвращает:
        List[Item]: список кортежей (вес, стоимость)
    """
    items = []
    for _ in range(n):
        weight = random.randint(1, max_weight)
        value = random.randint(1, max_value)
        items.append((weight, value))
    return items


def generate_tricky_case_1() -> Tuple[List[Item], int]:
    """
    Провокационный набор №1: жадный алгоритм ошибается, потому что
    предмет с высокой удельной стоимостью занимает почти весь рюкзак,
    а два других в сумме дают больше.

    Возвращает:
        Tuple[List[Item], int]: (список предметов, вместимость рюкзака)
    """
    # Вместимость рюкзака
    capacity = 10
    items = [
        (6, 30),   # удельная стоимость 5.0
        (5, 25),   # удельная стоимость 5.0
        (5, 24)    # удельная стоимость 4.8
    ]
    return items, capacity


def generate_tricky_case_2() -> Tuple[List[Item], int]:
    """
    Провокационный набор №2: два лёгких предмета дают больше, чем один тяжёлый.
    """
    capacity = 100
    items = [
        (51, 100),  # уд. ~1.96
        (50, 90),   # уд. 1.8
        (50, 90)    # уд. 1.8
    ]
    return items, capacity


def generate_tricky_case_3() -> Tuple[List[Item], int]:
    """
    Провокационный набор №3: специально сгенерированный с близкими удельными стоимостями.
    """
    capacity = 20
    items = [
        (19, 95),   # уд. 5.0
        (10, 49),   # уд. 4.9
        (10, 49)    # уд. 4.9
    ]
    return items, capacity


def get_all_tricky_cases() -> List[Tuple[List[Item], int]]:
    """
    Возвращает все провокационные наборы для тестирования.
    """
    return [
        generate_tricky_case_1(),
        generate_tricky_case_2(),
        generate_tricky_case_3()
    ]