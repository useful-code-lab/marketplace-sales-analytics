from generator import generate_mock_data
from pipeline import SeniorDataPipeline
import os

def main():
    if not os.path.exists('raw_orders.csv'):
        generate_mock_data()
        
    pipeline = SeniorDataPipeline(file_path='raw_orders.csv')
    
    # Расширяем нашу красивую Senior-цепочку
    processed_df = (pipeline
                    .load_data()
                    .clean_and_optimize()
                    .run_rfm_analysis()  # <-- Добавили аналитику
                    .detect_anomalies()  # <-- Добавили детекцию фрода
                    .get_data())
    
    print("\n🚀 Фрагмент итоговой аналитической таблицы:")
    # Показываем ключевые столбцы для проверки
    cols_to_show = ['order_id', 'client_id', 'category', 'total_revenue', 'Client_Segment', 'is_anomaly']
    print(processed_df[cols_to_show].head(10))

if __name__ == "__main__":
    main()
