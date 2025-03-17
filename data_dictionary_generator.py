import json
import os
from datetime import datetime
import pandas as pd
from pathlib import Path
import numpy as np
from datetime import timedelta

class DataDictionaryGenerator:
    def __init__(self, data_dir: str = "datas"):
        self.data_dir = Path(data_dir)
        self.data_range_file = self.data_dir / "data_range.json"
        self.resume_tracker_file = self.data_dir / "resume_tracker.json"
        
    def load_data_range(self) -> dict:
        """data_range.json 파일을 로드합니다."""
        with open(self.data_range_file, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    def load_resume_tracker(self) -> dict:
        """resume_tracker.json 파일을 로드합니다."""
        with open(self.resume_tracker_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def analyze_dataframe(self, df: pd.DataFrame) -> dict:
        """데이터프레임의 특성을 분석합니다."""
        analysis = {
            "columns": df.columns.tolist(),
            "data_types": df.dtypes.astype(str).to_dict(),
            "row_count": len(df),
            "date_range": {
                "start": df['date'].min().strftime("%Y-%m-%d") if 'date' in df.columns else None,
                "end": df['date'].max().strftime("%Y-%m-%d") if 'date' in df.columns else None
            },
            "unique_symbols": len(df['symbol'].unique()) if 'symbol' in df.columns else None,
            "column_stats": {}
        }
        
        # 수치형 컬럼의 통계 정보
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            analysis["column_stats"][col] = {
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "mean": float(df[col].mean()),
                "std": float(df[col].std()),
                "null_count": int(df[col].isnull().sum())
            }
        
        return analysis
    
    def get_parquet_info(self, file_path: Path, market: str, collection_frequency: str) -> dict:
        """parquet 파일의 정보를 가져옵니다."""
        try:
            df = pd.read_parquet(file_path)
            analysis = self.analyze_dataframe(df)
            
            # resume_tracker에서 마지막 수집 날짜 확인
            resume_tracker = self.load_resume_tracker()
            last_fetch_date = resume_tracker[market]["last_fetch_date"] if market in resume_tracker else None
            
            analysis.update({
                "collection_frequency": collection_frequency,
                "api_call_interval": "5S",
                "last_fetch_date": last_fetch_date
            })
            return analysis
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return {}
    
    def generate_dictionary(self) -> dict:
        """데이터 사전을 생성합니다."""
        data_range = self.load_data_range()
        
        # 기본 구조 생성
        dictionary = {
            "metadata": {
                "description": "금융 시장 데이터 사전",
                "version": "1.0.0",
                "last_updated": datetime.now().strftime("%Y-%m-%d")
            },
            "data_collection_info": {
                "time_range": {
                    "start_date": data_range["start_date"],
                    "end_date": data_range["end_date"]
                },
                "data_format": "parquet"
            },
            "markets": {},
            "data_pipeline_info": {
                "collection": {
                    "method": "API 호출",
                    "data_format": "parquet",
                    "api_call_interval": "5S"  # API 호출 간격은 5초로 고정
                },
                "storage": {
                    "location": str(self.data_dir),
                    "file_naming": "{market_name}.parquet"
                }
            }
        }
        
        # 각 시장별 정보 추가
        for market, info in data_range["markets"].items():
            if info["file_exists"]:
                file_path = Path(info["file_path"])
                data_info = self.get_parquet_info(
                    file_path, 
                    market,
                    data_range["data_collection_frequency"]
                )
                
                if data_info:
                    dictionary["markets"][market] = {
                        "description": f"{market} 시장 데이터",
                        "file_name": f"{market}.parquet",
                        "data_analysis": data_info,
                        "file_info": {
                            "path": str(file_path),
                            "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                        }
                    }
        
        return dictionary
    
    def save_dictionary(self, dictionary: dict, output_file: str = "data_dictionary.json"):
        """데이터 사전을 JSON 파일로 저장합니다."""
        output_path = self.data_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dictionary, f, ensure_ascii=False, indent=2)
        print(f"데이터 사전이 {output_path}에 저장되었습니다.")

def main():
    generator = DataDictionaryGenerator()
    dictionary = generator.generate_dictionary()
    generator.save_dictionary(dictionary)

if __name__ == "__main__":
    main() 