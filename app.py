"""
FastAPI приложение для веб-интерфейса.
Предоставляет эндпоинты для запуска алгоритмов на случайных данных
и для получения уже сохранённых графиков.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os
import random

from data_generator import generate_random_items, get_all_tricky_cases
from algorithms import (
    brute_force,
    greedy,
    dynamic_programming,
    simulated_annealing
)

app = FastAPI(title="Knapsack Algorithms API")

# Раздача статики (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")


# Модель запроса для запуска алгоритмов
class RunRequest(BaseModel):
    n: int
    capacity: int
    use_tricky: bool = False  # если True, игнорируем n и capacity, используем провокационный набор


class AlgorithmResult(BaseModel):
    algorithm: str
    value: int
    selected: List[int]
    time_seconds: float
    iterations: Optional[int] = 0


@app.post("/run", response_model=List[AlgorithmResult])
async def run_algorithms(request: RunRequest):
    """
    Запускает все алгоритмы на сгенерированных данных и возвращает результаты.
    """
    if request.use_tricky:
        # Берём первый провокационный набор (можно выбрать случайный)
        cases = get_all_tricky_cases()
        if not cases:
            raise HTTPException(status_code=404, detail="No tricky cases available")
        items, capacity = random.choice(cases)
    else:
        if request.n <= 0:
            raise HTTPException(status_code=400, detail="n must be positive")
        items = generate_random_items(request.n, max_weight=100, max_value=100)
        capacity = request.capacity if request.capacity > 0 else sum(w for w, _ in items) // 2

    # Список алгоритмов для запуска
    algos = [
        ("greedy", greedy),
        ("DP", dynamic_programming),
        ("simulated_annealing", lambda it, cap: simulated_annealing(it, cap))
    ]
    # Добавляем перебор, если n <= 20
    if len(items) <= 20:
        algos.append(("brute_force", brute_force))

    results = []
    for name, func in algos:
        import time
        start = time.perf_counter()
        result = func(items, capacity)
        elapsed = time.perf_counter() - start

        if name == "simulated_annealing":
            value, selected, iterations = result
        else:
            value, selected = result
            iterations = 0

        results.append(AlgorithmResult(
            algorithm=name,
            value=value,
            selected=selected,
            time_seconds=elapsed,
            iterations=iterations
        ))

    return results


@app.get("/plots")
async def get_plots():
    """
    Возвращает список доступных графиков (PNG) для отображения.
    """
    plots_dir = "plots"
    if not os.path.exists(plots_dir):
        return {"plots": []}
    files = [f for f in os.listdir(plots_dir) if f.endswith('.png')]
    return {"plots": files}


@app.get("/plot/{filename}")
async def get_plot(filename: str):
    """
    Отдаёт файл графика.
    """
    filepath = os.path.join("plots", filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Plot not found")
    return FileResponse(filepath, media_type="image/png")


@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Отдаёт HTML-страницу интерфейса.
    """
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()