import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json
import logging
from pathlib import Path
from binance.client import Client
import time

# 환경 변수 로드
load_dotenv()

# 로깅 설정
log_dir = Path('fund_bot/logs')
log_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=str(log_dir / 'error_log.txt'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class CryptoDataFetcher:
    def __init__(self):
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_API_SECRET')
        self.client = Client(self.api_key, self.api_secret)
        self.data_dir = Path('fund_bot/data')
        self.tracker_file = self.data_dir / 'resume_tracker.json'
        
        # 디렉토리 생성
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 진행 상태 추적 파일 초기화
        if not self.tracker_file.exists():
            self._init_tracker()

    def _init_tracker(self):
        """진행 상태 추적 파일 초기화"""
        tracker_data = {
            'crypto': {
                'last_fetch_date': None,
                'symbols': [
                    'BTCUSDT',  # 비트코인
                    'ETHUSDT',  # 이더리움
                    'BNBUSDT',  # 바이낸스 코인
                    'XRPUSDT',  # 리플
                    'ADAUSDT'   # 카르다노
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
        """암호화폐 데이터 수집"""
        try:
            tracker = self._load_tracker()
            if 'crypto' not in tracker:
                tracker['crypto'] = {
                    'last_fetch_date': None,
                    'symbols': [
                        'BTCUSDT', 'ETHUSDT', 'BNBUSDT',
                        'XRPUSDT', 'ADAUSDT'
                    ]
                }
            last_fetch = tracker['crypto']['last_fetch_date']
            
            # 날짜 설정
            if not start_date:
                start_date = last_fetch or (datetime.now() - timedelta(days=3650)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')

            # Binance API는 밀리초 단위의 타임스탬프 사용
            start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
            end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)

            all_data = []
            
            # 각 암호화폐별 데이터 수집
            for symbol in tracker['crypto']['symbols']:
                try:
                    klines = self.client.get_historical_klines(
                        symbol,
                        Client.KLINE_INTERVAL_1MONTH,
                        start_ts,
                        end_ts
                    )
                    
                    if klines:
                        df = pd.DataFrame(klines, columns=[
                            'timestamp', 'open', 'high', 'low', 'close', 'volume',
                            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                            'taker_buy_quote', 'ignore'
                        ])
                        
                        # 데이터 전처리
                        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
                        df['symbol'] = symbol
                        df = df[['date', 'symbol', 'open', 'high', 'low', 'close', 'volume']]
                        df = df.astype({
                            'open': float,
                            'high': float,
                            'low': float,
                            'close': float,
                            'volume': float
                        })
                        
                        all_data.append(df)
                        logging.info(f"Successfully fetched {symbol} from {start_date} to {end_date}")
                        time.sleep(1)  # API 제한 고려
                    
                except Exception as e:
                    logging.error(f"Error fetching {symbol}: {str(e)}")
                    continue

            if all_data:
                # DataFrame 생성 및 전처리
                df = pd.concat(all_data, ignore_index=True)
                
                # 기존 데이터가 있다면 병합
                existing_file = self.data_dir / 'crypto.parquet'
                if existing_file.exists():
                    existing_df = pd.read_parquet(existing_file)
                    df = pd.concat([existing_df, df]).drop_duplicates()
                
                # Parquet 파일로 저장
                df.to_parquet(self.data_dir / 'crypto.parquet')
                
                # 진행 상태 업데이트
                tracker['crypto']['last_fetch_date'] = end_date
                self._save_tracker(tracker)
                
                logging.info(f"Successfully saved crypto data from {start_date} to {end_date}")
                return True
            
            return False

        except Exception as e:
            logging.error(f"Error in fetch_data: {str(e)}")
            return False

if __name__ == "__main__":
    fetcher = CryptoDataFetcher()
    success = fetcher.fetch_data()
    print(f"Data collection {'successful' if success else 'failed'}") 