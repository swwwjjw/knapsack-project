# tests/test_benchmark.py
import pytest
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import csv
from unittest.mock import patch, MagicMock
from benchmark import run_benchmark, run_tricky_cases, CAPACITY_RATIO
from algorithms import dynamic_programming, brute_force

# ------------------------------------------------------------
# 1. Проверка точности вычислений accuracy
# ------------------------------------------------------------
def test_accuracy_calculation(tmp_path):
    """При истинном значении >0 accuracy должна быть (value/true_value)*100."""
    output = tmp_path / "test_accuracy.csv"
    # Используем n=5, где эталон - brute_force, и подмешиваем заведомо известные результаты
    with patch('benchmark.generate_random_items') as mock_gen:
        # Фиксированный набор: (3,5), (4,6), (2,3), (5,8), (1,2)
        mock_gen.return_value = [(3,5), (4,6), (2,3), (5,8), (1,2)]
        run_benchmark(n_values=[5], trials=1, capacity_ratio=0.5, output_file=str(output))
    
    with open(output) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Для DP и brute_force accuracy должно быть 100%
    for row in rows:
        if row['algorithm'] in ('DP', 'brute_force'):
            assert float(row['accuracy_percent']) == 100.0
        # Greedy может быть меньше или равно
        if row['algorithm'] == 'greedy':
            val = int(row['value'])
            true_val = int([r['value'] for r in rows if r['algorithm'] == 'DP'][0])
            if true_val > 0:
                expected_acc = (val / true_val) * 100
                assert abs(float(row['accuracy_percent']) - expected_acc) < 1e-6

# ------------------------------------------------------------
# 2. Случай, когда true_value == 0 (accuracy = 100 если value==0)
# ------------------------------------------------------------
def test_accuracy_when_optimum_zero(tmp_path):
    """Если оптимум 0, accuracy=100% только если алгоритм тоже дал 0."""
    output = tmp_path / "zero_opt.csv"
    with patch('benchmark.generate_random_items') as mock_gen:
        # Все предметы слишком тяжёлые для рюкзака
        mock_gen.return_value = [(10, 5), (12, 6)]
        run_benchmark(n_values=[2], trials=1, capacity_ratio=0.1, output_file=str(output))
    
    with open(output) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    for row in rows:
        if int(row['value']) == 0:
            assert float(row['accuracy_percent']) == 100.0
        else:
            assert float(row['accuracy_percent']) == 0.0

# ------------------------------------------------------------
# 4. Обработка пустого списка N_VALUES
# ------------------------------------------------------------
def test_empty_n_values(tmp_path):
    """Если n_values пуст, функция не должна падать, и CSV будет только с заголовком."""
    output = tmp_path / "empty.csv"
    run_benchmark(n_values=[], trials=1, output_file=str(output))
    with open(output) as f:
        reader = csv.reader(f)
        rows = list(reader)
    assert rows == [['n', 'trial', 'algorithm', 'time_seconds', 'value', 'accuracy_percent', 'iterations']]

# ------------------------------------------------------------
# 5. run_tricky_cases создаёт CSV с ожидаемыми столбцами
# ------------------------------------------------------------
def test_run_tricky_cases_creates_file(tmp_path):
    output = tmp_path / "tricky.csv"
    run_tricky_cases(output_file=str(output))
    assert output.exists()
    with open(output) as f:
        reader = csv.reader(f)
        header = next(reader)
    assert header == ['case_id', 'n', 'capacity', 'algorithm', 'value', 'selected_items', 'time_seconds', 'iterations']
    # Должны быть строки для всех кейсов и алгоритмов
    with open(output) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    # Для 3-х tricky cases, каждый по 4 алгоритма = 12 строк
    assert len(rows) == 3 * 4

# ------------------------------------------------------------
# 6. Изоляция времени: проверка, что замер времени происходит
# ------------------------------------------------------------
def test_timing_is_recorded(tmp_path):
    output = tmp_path / "timing.csv"
    counter = itertools.count(0, 0.01)
    with patch('benchmark.time.perf_counter', side_effect=counter):
        with patch('benchmark.generate_random_items') as mock_gen:
            mock_gen.return_value = [(2, 3), (3, 4)]
            run_benchmark(n_values=[2], trials=1, capacity_ratio=0.5, output_file=str(output))
    
    with open(output) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    for row in rows:
        assert float(row['time_seconds']) > 0

# ------------------------------------------------------------
# 7. Проверка, что capacity не может быть < 1
# ------------------------------------------------------------
def test_capacity_at_least_one(tmp_path):
    output = tmp_path / "cap.csv"
    with patch('benchmark.generate_random_items') as mock_gen:
        # Суммарный вес 2, при capacity_ratio=0.1 будет 0, функция должна сделать 1
        mock_gen.return_value = [(1,1), (1,1)]
        run_benchmark(n_values=[2], trials=1, capacity_ratio=0.01, output_file=str(output))
    # Проверяем, что в CSV записаны результаты, не упали с ошибкой
    with open(output) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) > 0
    # Дополнительно можно проверить, что capacity было действительно 1, но в CSV нет поля capacity.