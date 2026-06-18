# tests/test_data_generator.py
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from data_generator import (
    generate_random_items,
    generate_tricky_case_1,
    generate_tricky_case_2,
    generate_tricky_case_3,
    get_all_tricky_cases,
)

def test_generate_random_items_length():
    items = generate_random_items(10)
    assert len(items) == 10

def test_generate_random_items_range():
    items = generate_random_items(5, max_weight=50, max_value=200)
    for w, v in items:
        assert 1 <= w <= 50
        assert 1 <= v <= 200

def test_generate_tricky_case_1_known_optimum():
    items, capacity = generate_tricky_case_1()
    # Оптимум: взять два предмета (5,25) и (5,24) = 49, вес 10
    from algorithms import brute_force
    opt_val, _ = brute_force(items, capacity)
    assert opt_val == 49  # жадный даст 30

def test_generate_tricky_case_2_known_optimum():
    items, capacity = generate_tricky_case_2()
    # Оптимум: два предмета 50+50 = 90+90 = 180, вес 100
    from algorithms import brute_force
    opt_val, _ = brute_force(items, capacity)
    assert opt_val == 180

def test_get_all_tricky_cases_count():
    cases = get_all_tricky_cases()
    assert len(cases) == 3
    for items, cap in cases:
        assert cap > 0
        assert all(w > 0 and v > 0 for w, v in items)