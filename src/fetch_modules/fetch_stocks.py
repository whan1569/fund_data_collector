import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json
import logging
from pathlib import Path
import time
from .config import data_dir, TRACKER_FILE, config, get_logger

# 환경 변수 로드
load_dotenv()

# 모듈별 로거 가져오기
logger = get_logger('fetch_stocks')

class StockDataFetcher:
    def __init__(self):
        self.data_dir = data_dir
        self.tracker_file = TRACKER_FILE
        
        # 진행 상태 추적 파일 초기화
        if not self.tracker_file.exists():
            self._init_tracker()

    def _init_tracker(self):
        """진행 상태 추적 파일 초기화"""
        tracker_data = {
            'stocks': {
                'last_fetch_date': None,
                'symbols': [
                    '^GSPC',  # S&P 500
                    '^DJI',   # 다우존스
                    '^IXIC',  # 나스닥
                    '^FTSE',  # FTSE 100
                    '^N225'   # 닛케이 225
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
        """주식 데이터 수집"""
        try:
            tracker = self._load_tracker()
            if 'stocks' not in tracker:
                tracker['stocks'] = {
                    'last_fetch_date': None,
                    'symbols': [
                        '^GSPC', '^DJI', '^IXIC', '^FTSE', '^N225'
                    ]
                }
            last_fetch = tracker['stocks']['last_fetch_date']
            
            # 날짜 설정
            if not start_date:
                start_date = last_fetch or (datetime.now() - timedelta(days=3650)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')

            all_data = []
            
            # 각 지수별 데이터 수집
            for symbol in tracker['stocks']['symbols']:
                try:
                    ticker = yf.Ticker(symbol)
                    df = ticker.history(
                        start=start_date,
                        end=end_date,
                        interval=config.get_yfinance_interval()
                    )
                    
                    if not df.empty:
                        df = df.reset_index()
                        df['symbol'] = symbol
                        all_data.append(df)
                        logger.info(f"Successfully fetched {symbol} from {start_date} to {end_date}")
                        time.sleep(1)  # API 제한 고려
                    
                except Exception as e:
                    logger.error(f"Error fetching {symbol}: {str(e)}")
                    continue

            if all_data:
                # DataFrame 생성 및 전처리
                df = pd.concat(all_data, ignore_index=True)
                df = df.rename(columns={
                    'Date': 'date',
                    'Open': 'open',
                    'High': 'high',
                    'Low': 'low',
                    'Close': 'close',
                    'Volume': 'volume'
                })
                
                # 기존 데이터가 있다면 병합
                existing_file = self.data_dir / 'stocks.parquet'
                if existing_file.exists():
                    existing_df = pd.read_parquet(existing_file)
                    df = pd.concat([existing_df, df]).drop_duplicates()
                
                # Parquet 파일로 저장
                df.to_parquet(self.data_dir / 'stocks.parquet')
                
                # 진행 상태 업데이트
                tracker['stocks']['last_fetch_date'] = end_date
                self._save_tracker(tracker)
                
                logger.info(f"Successfully saved stocks data from {start_date} to {end_date}")
                return True
            
            return False

        except Exception as e:
            logger.error(f"Error in fetch_data: {str(e)}")
            return False

    def save_data(self, data):
        """데이터 저장"""
        try:
            # 데이터 저장
            data.to_parquet(self.data_dir / 'stocks.parquet')
            return True
        except Exception as e:
            logger.error(f"Error saving stocks data: {str(e)}")
            return False

if __name__ == "__main__":
    fetcher = StockDataFetcher()
    success = fetcher.fetch_data()
    print(f"Data collection {'successful' if success else 'failed'}") 