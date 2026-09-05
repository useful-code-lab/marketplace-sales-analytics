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

    def run_rfm_analysis(self, current_date=None) -> 'SeniorDataPipeline':
        """Шаг 3: Профессиональный RFM-анализ клиентов"""
        print("📊 Запуск RFM-анализа клиентов...")
        
        # Если дата не задана, берем самый свежий день в данных + 1 день
        if current_date is None:
            current_date = self.df['order_date'].max() + pd.Timedelta(days=1)
            
        # Агрегируем данные по каждому клиенту
        rfm = self.df.groupby('client_id').agg({
            'order_date': lambda x: (current_date - x.max()).days, # Recency (Давность покупки)
            'order_id': 'nunique',                                # Frequency (Частота покупок)
            'total_revenue': 'sum'                                # Monetary (Сумма покупок)
        }).rename(columns={
            'order_date': 'Recency',
            'order_id': 'Frequency',
            'total_revenue': 'Monetary'
        })
        
        # Разбиваем клиентов на 4 группы по квантилям (от 1 до 4)
        # Для давности (Recency) меньший срок — это лучше (ставим 4 балла), поэтому инвертируем шкалу
        rfm['R'] = pd.qcut(rfm['Recency'], q=4, labels=[4, 3, 2, 1]).astype(int)
        # Из-за специфики распределения частоты (Frequency) используем rank(method='first'), чтобы избежать ошибок дублирования границ квантилей
        rfm['F'] = pd.qcut(rfm['Frequency'].rank(method='first'), q=4, labels=[1, 2, 3, 4]).astype(int)
        rfm['M'] = pd.qcut(rfm['Monetary'], q=4, labels=[1, 2, 3, 4]).astype(int)
        
        # Объединяем оценки в один код сегмента
        rfm['RFM_Score'] = rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str)
        
        # Создаем понятные бизнесу текстовые сегменты
        def segment_client(row):
            if row['RFM_Score'] == '444':
                return 'VIP-клиенты'
            elif row['R'] == 4:
                return 'Новые активные'
            elif row['F'] == 4 and row['M'] == 4:
                # Покупают много и часто, но давно не заходили
                return 'В зоне риска (Лояльные теряются)'
            elif row['R'] == 1 and row['F'] == 1:
                return 'Ушедшие (Спящие)'
            else:
                return 'Постоянные середнячки'
                
        rfm['Client_Segment'] = rfm.apply(segment_client, axis=1)
        
        # Переносим результаты обратно в наш основной DataFrame
        self.df = self.df.merge(
            rfm['Client_Segment'], 
            on='client_id', 
            how='left'
        )
        print(f"   - Выделено сегментов клиентов: {rfm['Client_Segment'].value_counts().to_dict()}")
        return self

    def detect_anomalies(self) -> 'SeniorDataPipeline':
        """Шаг 4: Поиск фрода и аномалий через правило 3-х сигм внутри категорий"""
        print("🕵️‍♂️ Поиск аномальных транзакций...")
        
        # Считаем среднее и стандартное отклонение для каждой категории товаров отдельно
        stats = self.df.groupby('category', observed=False)['total_revenue'].agg(['mean', 'std']).reset_index()
        
        # Объединяем статистику с основным датафреймом
        temp_df = self.df.merge(stats, on='category', how='left')
        
        # Правило 3-х сигм: всё, что отклоняется от среднего больше чем на 3 стандартных отклонения — аномалия
        is_anomaly = temp_df['total_revenue'] > (temp_df['mean'] + 3 * temp_df['std'])
        
        # Записываем метку в основной DataFrame
        self.df['is_anomaly'] = is_anomaly.astype(int)
        
        anomalies_count = self.df['is_anomaly'].sum()
        print(f"   - Обнаружено подозрительных заказов: {anomalies_count}")
        return self

