import os
import sys
from datetime import datetime, timedelta
import logging
import time
from dotenv import load_dotenv
import json
from pathlib import Path

# 환경 변수 로드
load_dotenv()

# 프로젝트 루트 디렉토리 설정
current_dir = Path(__file__).parent
project_root = current_dir.parent

# 디렉토리 설정
data_dir = project_root / 'datas'
log_dir = project_root / 'logs'
report_dir = project_root / 'reports'

# 디렉토리 생성
for directory in [data_dir, log_dir, report_dir]:
    directory.mkdir(parents=True, exist_ok=True)

# 로깅 설정
logging.basicConfig(
    filename=str(log_dir / 'collection_log.txt'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 데이터 수집 모듈 임포트
sys.path.append(str(current_dir))

from fetch_modules.fetch_stocks import StockDataFetcher
from fetch_modules.fetch_commodities import CommodityDataFetcher
from fetch_modules.fetch_bonds import BondDataFetcher
from fetch_modules.fetch_forex import ForexDataFetcher
from fetch_modules.fetch_crypto import CryptoDataFetcher
from fetch_modules.fetch_real_estate import RealEstateDataFetcher

def parse_time_interval(interval_str):
    """시간 간격 문자열을 초 단위로 변환"""
    if not interval_str:
        return 5  # 기본값 5초
    
    try:
        value = float(interval_str[:-1])
        unit = interval_str[-1].upper()
        
        if unit == 'S':  # 초
            return int(value)
        elif unit == 'M':  # 분
            return int(value * 60)
        elif unit == 'H':  # 시간
            return int(value * 3600)
        elif unit == 'D':  # 일
            return int(value * 86400)
        elif unit == 'W':  # 주
            return int(value * 604800)
        elif unit == 'MO':  # 달
            return int(value * 2592000)  # 30일 기준
        elif unit == 'Y':  # 년
            return int(value * 31536000)
        else:
            raise ValueError(f"지원하지 않는 시간 단위입니다: {unit}")
    except (ValueError, IndexError):
        print(f"잘못된 시간 형식입니다. 기본값 5초를 사용합니다.")
        return 5

class DataCollectionManager:
    def __init__(self, start_date=None, end_date=None, save_interval=5):
        """
        데이터 수집 관리자 초기화
        
        Args:
            start_date (str): 데이터 수집 시작일 (YYYY-MM-DD 형식)
            end_date (str): 데이터 수집 종료일 (YYYY-MM-DD 형식)
            save_interval (int): 데이터 저장 간격 (초)
        """
        # 날짜 설정
        if start_date is None:
            self.start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        else:
            self.start_date = start_date
            
        if end_date is None:
            self.end_date = datetime.now().strftime('%Y-%m-%d')
        else:
            self.end_date = end_date
            
        self.save_interval = save_interval
        
        # 데이터 수집기 초기화
        self.collectors = {
            'stocks': StockDataFetcher(),
            'commodities': CommodityDataFetcher(),
            'bonds': BondDataFetcher(),
            'forex': ForexDataFetcher(),
            'crypto': CryptoDataFetcher(),
            'real_estate': RealEstateDataFetcher()
        }
        
        # 진행 상황 추적
        self.total_markets = len(self.collectors)
        self.completed_markets = 0

    def collect_all_data(self):
        """모든 시장 데이터 수집"""
        print(f"\n데이터 수집 시작: {self.start_date} ~ {self.end_date}")
        print("=" * 50)
        
        for market, collector in self.collectors.items():
            try:
                print(f"\n[{self.completed_markets + 1}/{self.total_markets}] {market} 데이터 수집 중...")
                success = collector.fetch_data(self.start_date, self.end_date)
                
                if success:
                    print(f"✓ {market} 데이터 수집 완료")
                    logging.info(f"Successfully collected {market} data")
                else:
                    print(f"✗ {market} 데이터 수집 실패")
                    logging.error(f"Failed to collect {market} data")
                
                self.completed_markets += 1
                print(f"진행률: {self.completed_markets}/{self.total_markets} ({(self.completed_markets/self.total_markets*100):.1f}%)")
                
                # API 제한 고려
                time.sleep(self.save_interval)
                
            except Exception as e:
                print(f"✗ {market} 데이터 수집 중 오류 발생: {str(e)}")
                logging.error(f"Error in {market} data collection: {str(e)}")
                continue

    def save_data_range(self):
        """데이터 범위 정보 저장"""
        range_file = data_dir / 'data_range.json'
        range_info = {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'markets': {}
        }
        
        # 각 시장별 데이터 범위 확인
        for market in self.collectors.keys():
            file_path = data_dir / f'{market}.parquet'
            if file_path.exists():
                range_info['markets'][market] = {
                    'file_exists': True,
                    'file_path': str(file_path)
                }
            else:
                range_info['markets'][market] = {
                    'file_exists': False,
                    'file_path': str(file_path)
                }
        
        with open(range_file, 'w', encoding='utf-8') as f:
            json.dump(range_info, f, ensure_ascii=False, indent=2)
        print("\n데이터 범위 정보가 저장되었습니다.")

    def generate_report(self):
        """수집 결과 보고서 생성"""
        report_dir = project_root / 'reports'
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = report_dir / f'collection_report_{datetime.now().strftime("%Y%m%d")}.txt'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"데이터 수집 보고서 ({datetime.now().strftime('%Y-%m-%d')})\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"수집 기간: {self.start_date} ~ {self.end_date}\n")
            f.write(f"저장 간격: {self.save_interval}초\n")
            f.write(f"수집 완료율: {self.completed_markets}/{self.total_markets} ({(self.completed_markets/self.total_markets*100):.1f}%)\n\n")
            
            # 각 시장별 데이터 파일 확인
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
        # 사용자 입력 받기
        print("데이터 수집 설정을 입력하세요 (기본값을 사용하려면 Enter를 누르세요):")
        print("시간 단위: S(초), M(분), H(시간), D(일), W(주), MO(달), Y(년)")
        start_date = input("시작일 (YYYY-MM-DD): ").strip() or None
        end_date = input("종료일 (YYYY-MM-DD): ").strip() or None
        save_interval = input("저장 간격 (예: 5S, 1M, 1H, 1D, 1W, 1MO, 1Y): ").strip()
        save_interval = parse_time_interval(save_interval)
        
        # 데이터 수집 실행
        manager = DataCollectionManager(
            start_date=start_date,
            end_date=end_date,
            save_interval=save_interval
        )
        manager.collect_all_data()
        manager.save_data_range()  # 데이터 범위 정보 저장
        manager.generate_report()
        print("\n데이터 수집이 완료되었습니다. 보고서를 확인해주세요.")
        
    except Exception as e:
        logging.error(f"Error in main execution: {str(e)}")
        print(f"오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    main() 