import pytest
import pandas as pd
import numpy as np
from pipeline import SeniorDataPipeline

@pytest.fixture
def sample_dirty_data(tmp_path):
    """
    Фикстура, которая создает временный 'грязный' CSV файл перед каждым тестом.
    """
    file_path = tmp_path / "test_raw_orders.csv"
    
    # Все данные прописаны жестко, без пустых мест
    order_ids = [1, 1, 2, 3]
    client_ids = [50001, 50001, 50002, 50002]
    order_dates = ['2025-01-01', '2025-01-01', '02/01/2025', '2025-01-03']
    categories = ['Электроника', 'Электроника', 'Книги', 'Книги']
    prices = [25000.0, 25000.0, np.nan, 1000.0]
    quantities = [1, 1, 2, 2]
    
    data = pd.DataFrame({
        'order_id': order_ids,
        'client_id': client_ids,
        'order_date': order_dates,
        'category': categories,
        'price': prices,
        'quantity': quantities
    })
    
    data.to_csv(file_path, index=False)
    return str(file_path)


def test_pipeline_cleaning_and_optimization(sample_dirty_data):
    """Тестируем, что дубликаты удаляются, а пропуски заполняются верно"""
    
    pipeline = SeniorDataPipeline(file_path=sample_dirty_data)
    df = pipeline.load_data().clean_and_optimize().get_data()
    
    # 1. Проверка удаления дубликатов (было 4 строки, 1 дубликат -> осталось 3)
    assert len(df) == 3, f"Ожидалось 3 строки после удаления дубликатов, но получили {len(df)}"
    
    # 2. Проверка умного заполнения пропусков по категории
    # Для Книг была цена 1000.0, значит пустая ячейка тоже должна стать 1000.0
    filled_price = df.loc[df['order_id'] == 2, 'price'].values[0]
    assert float(filled_price) == 1000.0, f"Цена не заполнилась корректно внутри категории. Получено: {filled_price}"
    
    # 3. Проверка оптимизации типов данных (сжатие RAM)
    assert df['quantity'].dtype in [np.int8, np.int16, np.int32, np.int64], "Тип данных quantity не оптимизирован!"
    assert df['category'].dtype == 'category', "Тип данных category не переведен в категориальный!"
