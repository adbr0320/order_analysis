import logging
from pathlib import Path

import pandas as pd


class OrderAnalyzer:
    """Читает все CSV с заказами из папки и считает метрики по доставленным"""

    def __init__(self, data_dir, reports_dir, logs_dir, report_filename,
                 log_filename, status_column, status_value, amount_column):
        self.data_dir = Path(data_dir)
        self.reports_dir = Path(reports_dir)
        self.logs_dir = Path(logs_dir)
        self.report_filename = report_filename
        self.log_filename = log_filename
        self.status_column = status_column
        self.status_value = status_value
        self.amount_column = amount_column
        self._setup_logging()

    def _setup_logging(self):
        self.logs_dir.mkdir(exist_ok=True)
        # в errors.log пишутся только ошибки, в консоль - всё;
        # mode='w' - каждый запуск начинает лог заново
        file_handler = logging.FileHandler(self.logs_dir / self.log_filename,
                                           mode='w', encoding='utf-8')
        file_handler.setLevel(logging.ERROR)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[file_handler, logging.StreamHandler()],
        )

    def find_files(self):
        if not self.data_dir.exists():
            logging.error(f'Папка {self.data_dir} не найдена')
            return []
        files = sorted(self.data_dir.glob('*.csv'))
        logging.info(f'Найдено CSV-файлов: {len(files)}')
        return files

    def load_file(self, file_path):
        """Читает CSV, при проблеме с файлом пишет в лог и возвращает None"""
        name = file_path.name
        try:
            df = pd.read_csv(file_path)
        except pd.errors.EmptyDataError:
            logging.error(f'{name}: файл пустой')
            return None
        except pd.errors.ParserError as e:
            logging.error(f'{name}: файл повреждён ({e})')
            return None
        except UnicodeDecodeError:
            logging.error(f'{name}: файл не в UTF-8, прочитать не удалось')
            return None
        except Exception as e:
            logging.error(f'{name}: ошибка при чтении ({e})')
            return None

        # проверяю только колонки, которые нужны для расчёта
        needed = {self.status_column, self.amount_column}
        missing = needed - set(df.columns)
        if missing:
            logging.error(f'{name}: нет колонок {sorted(missing)}')
            return None
        if df.empty:
            logging.error(f'{name}: в файле только заголовок, данных нет')
            return None
        # если в суммах попался текст, astype(float) выдаст ValueError
        try:
            df[self.amount_column].astype(float)
        except ValueError:
            logging.error(f'{name}: в {self.amount_column} есть '
                          'нечисловые значения')
            return None
        return df

    def filter_delivered(self, df):
        return df[df[self.status_column] == self.status_value]

    def calculate_metrics(self, df):
        orders_count = len(df)
        total_revenue = df[self.amount_column].sum()
        # если доставленных нет, mean() даст NaN, в отчёте лучше 0
        if orders_count == 0:
            average_check = 0
        else:
            average_check = df[self.amount_column].mean()
        return {
            'total_revenue': round(float(total_revenue), 2),
            'average_check': round(float(average_check), 2),
            'orders_count': orders_count,
        }

    def process_file(self, file_path):
        df = self.load_file(file_path)
        if df is None:
            return None

        delivered = self.filter_delivered(df)
        metrics = self.calculate_metrics(delivered)
        logging.info(f'{file_path.name}: доставленных заказов '
                     f'{metrics["orders_count"]}')

        result = {'file_name': file_path.name}
        result.update(metrics)
        return result

    def save_report(self, results):
        report_path = self.reports_dir / self.report_filename
        try:
            self.reports_dir.mkdir(exist_ok=True)
            pd.DataFrame(results).to_csv(report_path, index=False)
        except OSError as e:
            logging.error(f'Не удалось сохранить отчёт: {e}')
            return None
        logging.info(f'Отчёт сохранён: {report_path}')
        return report_path

    def process_all_files(self):
        """Возвращает {'processed': ..., 'failed': ..., 'report_path': ...}"""
        results = []
        failed = 0

        for file_path in self.find_files():
            try:
                result = self.process_file(file_path)
            except Exception as e:
                # на случай ошибки, которую load_file не предусмотрел
                logging.error(f'{file_path.name}: {e}')
                result = None

            if result is None:
                failed += 1
            else:
                results.append(result)

        report_path = None
        if results:
            report_path = self.save_report(results)
        else:
            logging.error('Ни один файл не обработан, отчёт не создан')

        return {
            'processed': len(results),
            'failed': failed,
            'report_path': report_path,
        }
