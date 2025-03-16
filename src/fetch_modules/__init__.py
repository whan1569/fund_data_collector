"""
데이터 수집 모듈 패키지
"""

from .fetch_stocks import StockDataFetcher
from .fetch_commodities import CommodityDataFetcher
from .fetch_bonds import BondDataFetcher
from .fetch_forex import ForexDataFetcher
from .fetch_crypto import CryptoDataFetcher
from .fetch_real_estate import RealEstateDataFetcher

__all__ = [
    'StockDataFetcher',
    'CommodityDataFetcher',
    'BondDataFetcher',
    'ForexDataFetcher',
    'CryptoDataFetcher',
    'RealEstateDataFetcher'
]

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
logging.basicConfig(
    filename=str(log_dir / 'error_log.txt'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 공통 설정
TRACKER_FILE = data_dir / 'resume_tracker.json' 