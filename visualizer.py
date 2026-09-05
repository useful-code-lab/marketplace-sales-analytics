import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from logger_config import logger

def create_analytics_plots(df: pd.DataFrame):
    """
    Генерирует профессиональные графики на основе обработанных данных
    и сохраняет их в файлы.
    """
    logger.info("📊 Начало процесса визуализации данных...")
    
    # Устанавливаем красивый стиль графиков
    sns.set_theme(style="whitegrid")
    
    # --- График 1: Распределение выручки по сегментам клиентов ---
    plt.figure(figsize=(10, 6))
    
    # Считаем общую выручку для каждого сегмента
    segment_sales = df.groupby('Client_Segment', observed=False)['total_revenue'].sum().reset_index()
    # Сортируем для красоты
    segment_sales = segment_sales.sort_values(by='total_revenue', ascending=False)
    
    sns.barplot(
        x='total_revenue', 
        y='Client_Segment', 
        data=segment_sales, 
        palette='viridis',
        hue='Client_Segment',
        legend=False
    )
    
    plt.title('Распределение выручки маркетплейса по сегментам клиентов', fontsize=14, fontweight='bold')
    plt.xlabel('Общая выручка (руб.)', fontsize=12)
    plt.ylabel('Сегмент клиентов', fontsize=12)
    plt.tight_layout()
    
    # Сохраняем график на диск
    plot_path_1 = 'customer_segments_revenue.png'
    plt.savefig(plot_path_1, dpi=300)
    plt.close() # Закрываем фигуру, чтобы не забивать память
    logger.info(f"   - [Успех] График сегментов сохранен как: {plot_path_1}")
    
    # --- График 2: Аномальные транзакции по категориям ---
    plt.figure(figsize=(10, 6))
    
    # Считаем количество аномалий в каждой категории
    anomalies = df[df['is_anomaly'] == 1].groupby('category', observed=False).size().reset_index(name='count')
    
    sns.barplot(
        x='category', 
        y='count', 
        data=anomalies, 
        palette='flare',
        hue='category',
        legend=False
    )
    
    plt.title('Количество подозрительных (аномальных) заказов по категориям', fontsize=14, fontweight='bold')
    plt.xlabel('Категория товара', fontsize=12)
    plt.ylabel('Число аномалий (ед.)', fontsize=12)
    plt.xticks(rotation=15)
    plt.tight_layout()
    
    plot_path_2 = 'detected_anomalies.png'
    plt.savefig(plot_path_2, dpi=300)
    plt.close()
    logger.info(f"   - [Успех] График аномалий сохранен как: {plot_path_2}")
    
    print("\n🎨 Все графики успешно сгенерированы!")
