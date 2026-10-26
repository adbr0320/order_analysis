import config
from src.analyzer import OrderAnalyzer


def main():
    analyzer = OrderAnalyzer(
        data_dir=config.DATA_DIR,
        reports_dir=config.REPORTS_DIR,
        logs_dir=config.LOGS_DIR,
        report_filename=config.REPORT_FILENAME,
        log_filename=config.LOG_FILENAME,
        status_column=config.STATUS_COLUMN,
        status_value=config.DELIVERED_STATUS,
        amount_column=config.AMOUNT_COLUMN,
    )
    result = analyzer.process_all_files()

    print()
    print('Обработано файлов:', result['processed'])
    print('Файлов с ошибками:', result['failed'])


if __name__ == '__main__':
    main()
