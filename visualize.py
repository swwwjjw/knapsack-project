"""
Модуль визуализации результатов бенчмарка.
Читает CSV-файлы, строит графики с помощью matplotlib и сохраняет их в PNG.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

# Константы
RESULTS_DIR = "results"
BENCHMARK_CSV = os.path.join(RESULTS_DIR, "benchmark_results.csv")
PLOTS_DIR = "plots"


def load_benchmark_data(csv_path: str = BENCHMARK_CSV) -> pd.DataFrame:
    """Загружает данные из CSV в DataFrame."""
    return pd.read_csv(csv_path)


def plot_time_vs_n(df: pd.DataFrame, save_path: str = None) -> None:
    """
    Строит график зависимости времени выполнения от n для всех алгоритмов.
    По оси Y — логарифмическая шкала для наглядности.
    """
    # Группируем по n и алгоритму, усредняем время
    grouped = df.groupby(['n', 'algorithm'])['time_seconds'].mean().reset_index()

    plt.figure(figsize=(10, 6))
    for algo in grouped['algorithm'].unique():
        subset = grouped[grouped['algorithm'] == algo]
        plt.plot(subset['n'], subset['time_seconds'], marker='o', label=algo)

    plt.xlabel('Количество предметов (n)')
    plt.ylabel('Среднее время выполнения (сек)')
    plt.yscale('log')  # логарифмическая шкала
    plt.title('Зависимость времени выполнения от n')
    plt.grid(True, which="both", ls="--")
    plt.legend()
    plt.tight_layout()

    if save_path:
        os.makedirs(PLOTS_DIR, exist_ok=True)
        plt.savefig(save_path)
    else:
        plt.show()
    plt.close()


def plot_accuracy_vs_n(df: pd.DataFrame, save_path: str = None) -> None:
    """
    Строит график точности (в %) от n для жадного алгоритма и имитации отжига.
    DP и перебор дают 100% точность, их не включаем.
    """
    # Оставляем только greedy и simulated_annealing
    filtered = df[df['algorithm'].isin(['greedy', 'simulated_annealing'])]
    grouped = filtered.groupby(['n', 'algorithm'])['accuracy_percent'].mean().reset_index()

    plt.figure(figsize=(10, 6))
    for algo in grouped['algorithm'].unique():
        subset = grouped[grouped['algorithm'] == algo]
        plt.plot(subset['n'], subset['accuracy_percent'], marker='s', label=algo)

    plt.xlabel('Количество предметов (n)')
    plt.ylabel('Средняя точность (%)')
    plt.ylim(0, 105)
    plt.title('Точность приближённых алгоритмов (в % от оптимума)')
    plt.grid(True, ls="--")
    plt.legend()
    plt.tight_layout()

    if save_path:
        os.makedirs(PLOTS_DIR, exist_ok=True)
        plt.savefig(save_path)
    else:
        plt.show()
    plt.close()


def plot_iterations_vs_n(df: pd.DataFrame, save_path: str = None) -> None:
    """
    Строит график числа итераций имитации отжига от n.
    """
    # Берём только отжиг
    sa_df = df[df['algorithm'] == 'simulated_annealing']
    grouped = sa_df.groupby('n')['iterations'].mean().reset_index()

    plt.figure(figsize=(10, 6))
    plt.plot(grouped['n'], grouped['iterations'], marker='^', color='red')

    plt.xlabel('Количество предметов (n)')
    plt.ylabel('Среднее число итераций')
    plt.title('Число итераций имитации отжига')
    plt.grid(True, ls="--")
    plt.tight_layout()

    if save_path:
        os.makedirs(PLOTS_DIR, exist_ok=True)
        plt.savefig(save_path)
    else:
        plt.show()
    plt.close()


def run_all_plots() -> None:
    """Запускает построение всех трёх графиков."""
    if not os.path.exists(BENCHMARK_CSV):
        print(f"Файл {BENCHMARK_CSV} не найден. Сначала запустите benchmark.py.")
        return

    df = load_benchmark_data()

    # Создаём папку для графиков
    os.makedirs(PLOTS_DIR, exist_ok=True)

    plot_time_vs_n(df, save_path=os.path.join(PLOTS_DIR, 'time_vs_n.png'))
    plot_accuracy_vs_n(df, save_path=os.path.join(PLOTS_DIR, 'accuracy_vs_n.png'))
    plot_iterations_vs_n(df, save_path=os.path.join(PLOTS_DIR, 'iterations_vs_n.png'))

    print(f"Графики сохранены в папку {PLOTS_DIR}/")


if __name__ == "__main__":
    run_all_plots()