from pathlib import Path

# пути строим от папки проекта, чтобы run.py работал из любой текущей папки
BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / 'data'
REPORTS_DIR = BASE_DIR / 'reports'
LOGS_DIR = BASE_DIR / 'logs'

REPORT_FILENAME = 'summary_report.csv'
LOG_FILENAME = 'errors.log'

STATUS_COLUMN = 'status'
DELIVERED_STATUS = 'Delivered'
AMOUNT_COLUMN = 'total_amount'
