from generator import generate_mock_data
from pipeline import SeniorDataPipeline
from logger_config import logger
from visualizer import create_analytics_plots # <-- Импортируем наш новый модуль
import os

def main():
    logger.info("🚀 Старт аналитической платформы маркетплейса...")
    
    if not os.path.exists('raw_orders.csv'):
        logger.warning("⚠️ Файл 'raw_orders.csv' не найден. Запускаем генератор данных...")
        generate_mock_data()
        
    try:
        pipeline = SeniorDataPipeline(file_path='raw_orders.csv')
        
        # Получаем финальный DataFrame в переменную processed_df
        processed_df = (pipeline
                        .load_data()
                        .clean_and_optimize()
                        .run_rfm_analysis()
                        .detect_anomalies()
                        .export_reports()
                        .get_data()) # <-- Забираем очищенные данные
        
        # Передаем данные в модуль визуализации
        create_analytics_plots(processed_df)
                
        logger.info("🏁 Работа конвейера и визуализация успешно завершены!")
        
    except Exception as e:
        logger.critical(f"🚨 Работа системы аварийно прервана: {str(e)}")

if __name__ == "__main__":
    main()
