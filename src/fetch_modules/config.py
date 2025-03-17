import os
from pathlib import Path
import logging
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 프로젝트 루트 디렉토리 설정
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent

# 디렉토리 설정
data_dir = project_root / 'datas'
log_dir = project_root / 'logs'
report_dir = project_root / 'reports'

# 디렉토리 생성
for directory in [data_dir, log_dir, report_dir]:
    directory.mkdir(parents=True, exist_ok=True)

# 로깅 설정
def setup_logging():
    """중앙 로깅 설정"""
    logging.basicConfig(
        filename=str(log_dir / 'error_log.txt'),
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        encoding='utf-8'
    )

def get_logger(module_name: str) -> logging.Logger:
    """
    모듈별 로거 가져오기
    
    Args:
        module_name: 모듈 이름 (예: 'fetch_stocks', 'fetch_bonds' 등)
    
    Returns:
        logging.Logger: 설정된 로거 객체
    """
    logger = logging.getLogger(module_name)
    return logger

# 로깅 초기 설정 실행
setup_logging()

# 공통 설정
TRACKER_FILE = data_dir / 'resume_tracker.json'

# 데이터 수집 설정
class DataCollectionConfig:
    def __init__(self):
        self._interval = '1mo'  # 기본값
        self._start_date = None
        self._end_date = None
        self._data_dir = data_dir

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, value):
        self._interval = value

    def get_yfinance_interval(self):
        """yfinance API용 interval 형식"""
        # yfinance는 소문자 사용
        return self._interval.lower()

    def get_binance_interval(self):
        """Binance API용 interval 형식"""
        # Binance는 대문자 사용
        value = float(self._interval[:-1])
        unit = self._interval[-1].upper()
        
        if unit == 'D':
            return f"{int(value)}D"
        elif unit == 'W':
            return f"{int(value)}W"
        elif unit == 'M' and self._interval[-2] != 'o':  # 분(M)과 월(mo) 구분
            return f"{int(value)}M"
        elif unit == 'H':
            return f"{int(value)}H"
        elif self._interval.endswith('mo'):
            return '1M'  # Binance는 월간 데이터를 '1M'으로 표현
        return '1D'  # 기본값

    def get_fred_interval(self):
        """FRED API용 interval 형식"""
        # FRED는 소문자 한 글자 사용
        if self._interval.endswith('mo'):
            return 'm'
        elif self._interval.endswith('d'):
            return 'd'
        elif self._interval.endswith('w'):
            return 'w'
        elif self._interval.endswith('y'):
            return 'a'
        return 'd'  # 기본값

    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, value):
        self._start_date = value

    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, value):
        self._end_date = value

    @property
    def data_dir(self):
        return self._data_dir

# 전역 설정 객체 생성
config = DataCollectionConfig() 