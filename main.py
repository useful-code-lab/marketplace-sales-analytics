from generator import generate_mock_data
from pipeline import SeniorDataPipeline
import os

def main():
    print("🏁 Запуск аналитической платформы маркетплейса...\n")
    
    # Генерация данных, если их нет
    if not os.path.exists('raw_orders.csv'):
        generate_mock_data()
        
    # Инициализация пайплайна
    pipeline = SeniorDataPipeline(file_path='raw_orders.csv')
    
    # Идеальная, чистая Senior-цепочка вызовов (Method Chaining)
    pipeline.load_data() \
            .clean_and_optimize() \
            .run_rfm_analysis() \
            .detect_anomalies() \
            .export_reports()
            
    print("\n🎉 Проект успешно выполнен! Проверьте созданные файлы отчетов в папке проекта.")

if __name__ == "__main__":
    main()
