import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json
import logging
from pathlib import Path
import time
import fredapi
from .config import data_dir, TRACKER_FILE

# 환경 변수 로드
load_dotenv()

# 로깅 설정
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
log_dir = project_root / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=str(log_dir / 'error_log.txt'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BondDataFetcher:
    def __init__(self):
        self.api_key = os.getenv('FRED_API_KEY')
        self.fred = fredapi.Fred(api_key=self.api_key)
        self.data_dir = data_dir
        self.tracker_file = TRACKER_FILE
        
        # 진행 상태 추적 파일 초기화
        if not self.tracker_file.exists():
            self._init_tracker()

    def _init_tracker(self):
        """진행 상태 추적 파일 초기화"""
        tracker_data = {
            'bonds': {
                'last_fetch_date': None,
                'series': [
                    'DGS10',  # 10년 국채 금리
                    'DGS2',   # 2년 국채 금리
                    'DGS30',  # 30년 국채 금리
                    'BAA10Y', # 10년 회사채 금리
                    'AAA10Y'  # 10년 AAA 등급 회사채 금리
                ]
            }
        }
        with open(self.tracker_file, 'w') as f:
            json.dump(tracker_data, f, indent=4)

    def _load_tracker(self):
        """진행 상태 로드"""
        with open(self.tracker_file, 'r') as f:
            return json.load(f)

    def _save_tracker(self, tracker_data):
        """진행 상태 저장"""
        with open(self.tracker_file, 'w') as f:
            json.dump(tracker_data, f, indent=4)

    def fetch_data(self, start_date=None, end_date=None):
        """채권 데이터 수집"""
        try:
            tracker = self._load_tracker()
            if 'bonds' not in tracker:
                tracker['bonds'] = {
                    'last_fetch_date': None,
                    'series': [
                        'DGS10', 'DGS2', 'DGS30', 'BAA10Y', 'AAA10Y'
                    ]
                }
            last_fetch = tracker['bonds']['last_fetch_date']
            
            # 날짜 설정
            if not start_date:
                start_date = last_fetch or (datetime.now() - timedelta(days=3650)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')

            all_data = []
            
            # 각 시리즈별 데이터 수집
            for series in tracker['bonds']['series']:
                try:
                    df = self.fred.get_series(series, observation_start=start_date, observation_end=end_date)
                    
                    if not df.empty:
                        df = df.reset_index()
                        df.columns = ['date', 'value']
                        df['series'] = series
                        all_data.append(df)
                        logging.info(f"Successfully fetched {series} from {start_date} to {end_date}")
                        time.sleep(1)  # API 제한 고려
                    
                except Exception as e:
                    logging.error(f"Error fetching {series}: {str(e)}")
                    continue

            if all_data:
                # DataFrame 생성 및 전처리
                df = pd.concat(all_data, ignore_index=True)
                
                # 기존 데이터가 있다면 병합
                existing_file = self.data_dir / 'bonds.parquet'
                if existing_file.exists():
                    existing_df = pd.read_parquet(existing_file)
                    df = pd.concat([existing_df, df]).drop_duplicates()
                
                # Parquet 파일로 저장
                df.to_parquet(self.data_dir / 'bonds.parquet')
                
                # 진행 상태 업데이트
                tracker['bonds']['last_fetch_date'] = end_date
                self._save_tracker(tracker)
                
                logging.info(f"Successfully saved bonds data from {start_date} to {end_date}")
                return True
            
            return False

        except Exception as e:
            logging.error(f"Error in fetch_data: {str(e)}")
            return False

    def save_data(self, data):
        """데이터 저장"""
        try:
            # 데이터 저장
            data.to_parquet(self.data_dir / 'bonds.parquet')
            return True
        except Exception as e:
            logging.error(f"Error saving bonds data: {str(e)}")
            return False

if __name__ == "__main__":
    fetcher = BondDataFetcher()
    success = fetcher.fetch_data()
    print(f"Data collection {'successful' if success else 'failed'}") 