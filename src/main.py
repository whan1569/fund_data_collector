import os
import sys
from datetime import datetime, timedelta
import logging
from pathlib import Path
import time
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 로깅 설정
log_dir = Path('fund_bot/logs')
log_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=str(log_dir / 'collection_log.txt'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 데이터 수집 모듈 임포트
sys.path.append(str(Path(__file__).parent))
from fetch_modules.fetch_stocks import StockDataFetcher
from fetch_modules.fetch_commodities import CommodityDataFetcher
from fetch_modules.fetch_bonds import BondDataFetcher
from fetch_modules.fetch_forex import ForexDataFetcher
from fetch_modules.fetch_crypto import CryptoDataFetcher
from fetch_modules.fetch_real_estate import RealEstateDataFetcher

class DataCollectionManager:
    def __init__(self):
        self.start_date = (datetime.now() - timedelta(days=3650)).strftime('%Y-%m-%d')  # 10년 전
        self.end_date = datetime.now().strftime('%Y-%m-%d')
        self.collectors = {
            'stocks': StockDataFetcher(),
            'commodities': CommodityDataFetcher(),
            'bonds': BondDataFetcher(),
            'forex': ForexDataFetcher(),
            'crypto': CryptoDataFetcher(),
            'real_estate': RealEstateDataFetcher()
        }

    def collect_all_data(self):
        """모든 시장 데이터 수집"""
        logging.info(f"Starting data collection from {self.start_date} to {self.end_date}")
        
        for market, collector in self.collectors.items():
            try:
                logging.info(f"Starting {market} data collection...")
                success = collector.fetch_data(self.start_date, self.end_date)
                
                if success:
                    logging.info(f"Successfully collected {market} data")
                else:
                    logging.error(f"Failed to collect {market} data")
                
                # API 제한 고려
                time.sleep(5)
                
            except Exception as e:
                logging.error(f"Error in {market} data collection: {str(e)}")
                continue

    def generate_report(self):
        """수집 결과 보고서 생성"""
        report_dir = Path('fund_bot/reports')
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = report_dir / f'collection_report_{datetime.now().strftime("%Y%m%d")}.txt'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"데이터 수집 보고서 ({datetime.now().strftime('%Y-%m-%d')})\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"수집 기간: {self.start_date} ~ {self.end_date}\n\n")
            
            # 각 시장별 데이터 파일 확인
            data_dir = Path('fund_bot/data')
            for market in self.collectors.keys():
                file_path = data_dir / f'{market}.parquet'
                if file_path.exists():
                    f.write(f"{market}: 데이터 파일 존재\n")
                else:
                    f.write(f"{market}: 데이터 파일 없음\n")
            
            # 로그 파일에서 에러 확인
            log_file = log_dir / 'collection_log.txt'
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as log:
                    errors = [line for line in log if 'ERROR' in line]
                    if errors:
                        f.write("\n발생한 에러:\n")
                        for error in errors:
                            f.write(f"- {error.strip()}\n")

def main():
    try:
        manager = DataCollectionManager()
        manager.collect_all_data()
        manager.generate_report()
        print("데이터 수집이 완료되었습니다. 보고서를 확인해주세요.")
        
    except Exception as e:
        logging.error(f"Error in main execution: {str(e)}")
        print(f"오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    main() 