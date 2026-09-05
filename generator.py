import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_mock_data(num_rows=100000):
    """
    Генерирует сырые, 'грязные' данные для имитации реального продакшена.
    """
    np.random.seed(42) # Фиксируем случайность, чтобы результаты были одинаковыми
    
    # 1. Генерируем базовые ID
    order_ids = np.arange(1000, 1000 + num_rows)
    client_ids = np.random.randint(50000, 51000, size=num_rows)
    
    # 2. Генерируем даты (с подвохом: некоторые даты запишем текстом в разном формате)
    start_date = datetime(2025, 1, 1)
    date_pool = [start_date + timedelta(days=int(i)) for i in np.random.randint(0, 365, size=num_rows)]
    
    # 3. Категории товаров и цены
    categories = ['Электроника', 'Одежда', 'Книги', 'Дом', 'Красота']
    chosen_categories = np.random.choice(categories, size=num_rows, p=[0.3, 0.3, 0.1, 0.2, 0.1])
    
    # Базовые цены для категорий
    price_map = {'Электроника': 25000, 'Одежда': 3000, 'Книги': 800, 'Дом': 5000, 'Красота': 1500}
    base_prices = np.array([price_map[cat] for cat in chosen_categories], dtype=float)
    # Добавим случайный шум к ценам
    prices = base_prices * np.random.uniform(0.8, 1.2, size=num_rows)
    
    # Количество товара
    quantities = np.random.randint(1, 5, size=num_rows)
    
    # Собираем DataFrame
    df = pd.DataFrame({
        'order_id': order_ids,
        'client_id': client_ids,
        'order_date': date_pool,
        'category': chosen_categories,
        'price': prices,
        'quantity': quantities
    })
    
    # --- Портим данные (как в жизни!) ---
    
    # Добавляем дубликаты строк (5% дублей)
    duplicates = df.sample(frac=0.05)
    df = pd.concat([df, duplicates], ignore_index=True)
    
    # Вносим пропуски в колонку price (2% пропусков)
    df.loc[df.sample(frac=0.02).index, 'price'] = np.nan
    
    # Превращаем часть дат в строки разного формата, чтобы протестировать парсер
    string_date_idx = df.sample(frac=0.05).index
    df.loc[string_date_idx, 'order_date'] = df.loc[string_date_idx, 'order_date'].dt.strftime('%d/%m/%Y')

    # Сохраняем в CSV
    df.to_csv('raw_orders.csv', index=False)
    print(f"Файл 'raw_orders.csv' успешно создан. Строк: {len(df)}")

if __name__ == "__main__":
    generate_mock_data()
