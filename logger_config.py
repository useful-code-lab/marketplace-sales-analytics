import logging
import sys

def setup_logger():
    """
    Настраивает логирование: выводит сообщения в консоль 
    и одновременно записывает их в файл pipeline.log.
    """
    logger = logging.getLogger("SeniorPipeline")
    
    if logger.hasHandlers():
        return logger
        
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s | [%(levelname)s] | %(filename)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 1. Запись в файл
    file_handler = logging.FileHandler('pipeline.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 2. Вывод в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# Вот здесь мы его создаем, и именно его будут импортировать ДРУГИЕ файлы (pipeline.py и main.py)
logger = setup_logger()
