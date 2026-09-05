import pandas as pd
import numpy as np

class SeniorDataPipeline:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None

    def load_data(self) -> 'SeniorDataPipeline':
        """Шаг 1: Загрузка данных"""
        print("📥 Загрузка сырых данных...")
        # Читаем данные. order_date пока загружаем как строку (object), так как там разный формат
        self.df = pd.read_csv(self.file_path)
        return self

    def clean_and_optimize(self) -> 'SeniorDataPipeline':
        """Шаг 2: Очистка дубликатов, заполнение пропусков и оптимизация типов"""
        print("🧹 Запуск очистки и оптимизации памяти...")
        
        # 1. Удаление полных дубликатов (Senior-подход: сбрасываем индексы)
        initial_rows = len(self.df)
        self.df.drop_duplicates(inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        print(f"   - Удалено дубликатов: {initial_rows - len(self.df)}")

        # 2. Исправление дат (Парсим смешанные форматы: 2025-01-01 и 01/01/2025)
        # format='mixed' спасает проект от падения при разных форматах в одной колонке
        self.df['order_date'] = pd.to_datetime(self.df['order_date'], format='mixed')

        # 3. Умное заполнение пропусков в ценах
        # Вместо медианы по всему сайту, берем медиану ИМЕННО той категории, к которой принадлежит товар
        self.df['price'] = self.df.groupby('category')['price'].transform(lambda x: x.fillna(x.median()))

        # 4. Оптимизация типов данных (Уменьшаем потребление RAM в несколько раз)
        # Переводим категориальный текст в специальный тип 'category'
        self.df['category'] = self.df['category'].astype('category')
        
        # Сжимаем целые числа (вместо int64 используем меньшие подтипы)
        self.df['quantity'] = pd.to_numeric(self.df['quantity'], downcast='integer')
        self.df['client_id'] = pd.to_numeric(self.df['client_id'], downcast='integer')
        
        # Сжимаем числа с плавающей точкой
        self.df['price'] = pd.to_numeric(self.df['price'], downcast='float')

        # 5. Создаем вычисляемый бизнес-метрический столбец
        self.df['total_revenue'] = self.df['price'] * self.df['quantity']

        # Выводим отчет по памяти
        mem_usage = self.df.memory_usage(deep=True).sum() / (1024 ** 2)
        print(f"   - Очистка завершена. Текущий размер в памяти: {mem_usage:.2f} MB")
        
        return self

    def get_data(self) -> pd.DataFrame:
        """Возвращает обработанный DataFrame"""
        return self.df
