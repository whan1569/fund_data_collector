
## **📌 각 시장별 심리지표 & 데이터 소스**  

| **시장** | **심리지표** | **데이터 소스** |
|----------|------------|------------------|
| **주식** | Fear & Greed Index (투자 심리) | **CNN Fear & Greed Index API** |
|          | VIX (변동성 지수, 시장 불안감) | **CBOE VIX Index (Yahoo Finance API)** |
| **채권** | TED Spread (신용위험) | **FRED API** |
|          | 장단기 금리 스프레드 (경기 전망) | **FRED API (10Y-2Y Spread)** |
| **외환** | 달러 인덱스 (DXY) | **Yahoo Finance API** |
|          | 기관 투자자 포지션 (COT 리포트) | **CFTC Commitment of Traders (CFTC.gov)** |
| **암호화폐** | Crypto Fear & Greed Index | **Alternative.me API** |
|           | 온체인 데이터 (거래량, 지갑 이동) | **Glassnode API** |
| **원자재** | 원유 투기적 포지션 (COT 리포트) | **CFTC Commitment of Traders (CFTC.gov)** |
|          | 금 ETF 보유량 (투자 심리) | **World Gold Council, SPDR Gold Shares (GLD ETF)** |
| **부동산** | 주택 구매 심리 지수 | **NAHB Housing Market Index (FRED API)** |
|          | 모기지 신청 건수 | **MBA Mortgage Applications (FRED API)** |

---

## **📌 활용 방법**
- **CNN Fear & Greed Index** → 주식 시장 전체 심리 분석  
- **VIX (변동성 지수)** → 시장 불안감이 높을수록 위험 회피 가능성  
- **Crypto Fear & Greed Index** → 암호화폐 시장 과열/공포 측정  
- **COT 리포트 (선물 포지션 데이터)** → 외환 & 원자재 시장에서 기관 투자자의 방향성 파악  
- **금 ETF 보유량** → 금의 투자 수요 변화를 반영  
