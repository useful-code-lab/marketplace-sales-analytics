from generator import generate_mock_data
from pipeline import SeniorDataPipeline
import os

def main():
    # 1. Если файла с данными нет, генерируем его
    if not os.path.exists('raw_orders.csv'):
        generate_mock_data()
        
    # 2. Инициализируем и запускаем наш пайплайн
    pipeline = SeniorDataPipeline(file_path='raw_orders.csv')
    
    # Запускаем цепочку обработки
    processed_df = (pipeline
                    .load_data()
                    .clean_and_optimize()
                    .get_data())
    
    print("\n🚀 Первые 5 строк очищенных данных:")
    print(processed_df.head())

if __name__ == "__main__":
    main()
