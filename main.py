from generator import generate_mock_data
from pipeline import SeniorDataPipeline
from logger_config import logger # <-- Импортируем логгер сюда тоже
import os

def main():
    logger.info("🚀 Старт аналитической платформы маркетплейса...")
    
    if not os.path.exists('raw_orders.csv'):
        logger.warning("⚠️ Файл 'raw_orders.csv' не найден. Запускаем генератор данных...")
        generate_mock_data()
        
    try:
        pipeline = SeniorDataPipeline(file_path='raw_orders.csv')
        
        pipeline.load_data() \
                .clean_and_optimize() \
                .run_rfm_analysis() \
                .detect_anomalies() \
                .export_reports()
                
        logger.info("🏁 Работа конвейера успешно завершена!")
        
    except Exception as e:
        logger.critical(f"🚨 Работа системы аварийно прервана: {str(e)}")

if __name__ == "__main__":
    main()
