import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json
import logging
from pathlib import Path
from binance.client import Client
import time
from .config import data_dir, TRACKER_FILE, config, get_logger

# 환경 변수 로드
load_dotenv()

# 모듈별 로거 가져오기
logger = get_logger('fetch_crypto')

class CryptoDataFetcher:
    def __init__(self):
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_API_SECRET')
        self.client = Client(self.api_key, self.api_secret)
        self.data_dir = data_dir
        self.tracker_file = TRACKER_FILE
        
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
            if not self.api_key or not self.api_secret:
                logger.error("Binance API credentials not found")
                return False

            # 바이낸스 설립일 체크 (2017년 7월)
            binance_launch_date = '2017-07-01'
            if start_date and start_date < binance_launch_date:
                logger.warning(f"Requested start date ({start_date}) is before Binance launch date ({binance_launch_date}). Adjusting start date.")
                start_date = binance_launch_date

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
                start_date = last_fetch or binance_launch_date
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')

            # Binance API는 밀리초 단위의 타임스탬프 사용
            start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
            end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)

            all_data = []
            
            # 각 암호화폐별 데이터 수집
            for symbol in tracker['crypto']['symbols']:
                try:
                    # 기본 interval을 1일로 설정
                    interval = Client.KLINE_INTERVAL_1DAY
                    
                    # 만약 config에서 interval이 설정되어 있다면 사용
                    if hasattr(config, 'interval'):
                        interval_map = {
                            '1m': Client.KLINE_INTERVAL_1MINUTE,
                            '3m': Client.KLINE_INTERVAL_3MINUTE,
                            '5m': Client.KLINE_INTERVAL_5MINUTE,
                            '15m': Client.KLINE_INTERVAL_15MINUTE,
                            '30m': Client.KLINE_INTERVAL_30MINUTE,
                            '1h': Client.KLINE_INTERVAL_1HOUR,
                            '2h': Client.KLINE_INTERVAL_2HOUR,
                            '4h': Client.KLINE_INTERVAL_4HOUR,
                            '6h': Client.KLINE_INTERVAL_6HOUR,
                            '8h': Client.KLINE_INTERVAL_8HOUR,
                            '12h': Client.KLINE_INTERVAL_12HOUR,
                            '1d': Client.KLINE_INTERVAL_1DAY,
                            '3d': Client.KLINE_INTERVAL_3DAY,
                            '1w': Client.KLINE_INTERVAL_1WEEK,
                            '1mo': Client.KLINE_INTERVAL_1MONTH
                        }
                        interval = interval_map.get(config.interval.lower(), Client.KLINE_INTERVAL_1DAY)
                    
                    klines = self.client.get_historical_klines(
                        symbol,
                        interval,
                        start_ts,
                        end_ts
                    )
                    
                    if klines:
                        # 데이터 전처리
                        df = pd.DataFrame(klines, columns=[
                            'timestamp', 'open', 'high', 'low', 'close',
                            'volume', 'close_time', 'quote_volume', 'trades',
                            'buy_base_volume', 'buy_quote_volume', 'ignore'
                        ])
                        
                        # 필요한 컬럼만 선택
                        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
                        
                        # 데이터 타입 변환
                        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                        for col in ['open', 'high', 'low', 'close', 'volume']:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                        
                        # 컬럼명 변경
                        df = df.rename(columns={'timestamp': 'date'})
                        df['symbol'] = symbol
                        
                        all_data.append(df)
                        logger.info(f"Successfully fetched {symbol} from {start_date} to {end_date}")
                        time.sleep(1)  # API 제한 고려
                    else:
                        logger.warning(f"No data available for {symbol} in the specified date range")
                    
                except Exception as e:
                    logger.error(f"Error fetching {symbol}: {str(e)}")
                    continue

            if all_data:
                # DataFrame 생성 및 전처리
                df = pd.concat(all_data, ignore_index=True)
                
                # 기존 데이터가 있다면 병합
                existing_file = self.data_dir / 'crypto.parquet'
                if existing_file.exists():
                    existing_df = pd.read_parquet(existing_file)
                    df = pd.concat([existing_df, df]).drop_duplicates(subset=['date', 'symbol'])
                    df = df.sort_values(['symbol', 'date'])
                
                # Parquet 파일로 저장
                df.to_parquet(self.data_dir / 'crypto.parquet')
                
                # 진행 상태 업데이트
                tracker['crypto']['last_fetch_date'] = end_date
                self._save_tracker(tracker)
                
                logger.info(f"Successfully saved crypto data from {start_date} to {end_date}")
                return True
            else:
                logger.warning("No data was collected for any cryptocurrency")
                return False

        except Exception as e:
            logger.error(f"Error in fetch_data: {str(e)}")
            return False

    def save_data(self, data):
        """데이터 저장"""
        try:
            # 데이터 저장
            data.to_parquet(self.data_dir / 'crypto.parquet')
            return True
        except Exception as e:
            logger.error(f"Error saving crypto data: {str(e)}")
            return False

if __name__ == "__main__":
    fetcher = CryptoDataFetcher()
    success = fetcher.fetch_data()
    print(f"Data collection {'successful' if success else 'failed'}") 