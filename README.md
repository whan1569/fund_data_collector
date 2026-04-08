
# Fund Data Collector

An automated financial data collection system that gathers, processes, and stores data across multiple asset classes, including equities, commodities, bonds, forex, cryptocurrencies, and real estate.

Designed for scalable financial analysis, this tool transforms raw market data into structured datasets for research, portfolio tracking, and quantitative workflows.

---

## Project Structure

```mermaid
graph TD
    A[fund_data_collector] --> B[src]
    A --> C[datas]
    A --> D[logs]
    A --> E[reports]
    
    B --> F[main.py]
    B --> G[fetch_modules]
    
    G --> H[config.py]
    G --> I[fetch_stocks.py]
    G --> J[fetch_commodities.py]
    G --> K[fetch_bonds.py]
    G --> L[fetch_forex.py]
    G --> M[fetch_crypto.py]
    G --> N[fetch_real_estate.py]
    
    C --> O[stocks.parquet]
    C --> P[commodities.parquet]
    C --> Q[bonds.parquet]
    C --> R[forex.parquet]
    C --> S[crypto.parquet]
    C --> T[real_estate.parquet]
    C --> U[resume_tracker.json]
    
    D --> V[collection_log.txt]
    D --> W[error_log.txt]
    
    E --> X[collection_report_YYYYMMDD.txt]
````

---

## Features

* Automated data collection from multiple financial markets
* Data normalization and preprocessing pipeline
* Multi-asset coverage (stocks, commodities, bonds, forex, crypto, real estate)
* Structured storage using efficient formats (Parquet)
* Resume capability via tracking system
* Logging and reporting for monitoring and debugging

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/fund_data_collector.git
cd fund_data_collector
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set environment variables

Create a `.env` file and configure the following:

```
FRED_API_KEY=your_fred_api_key
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret
```

---

## Usage

```bash
python src/main.py
```

---

## Data Schema

### 1. Stocks (`stocks.parquet`)

* **Coverage**: Major indices (S&P 500, Dow Jones, NASDAQ, FTSE 100, Nikkei 225)
* **Columns**:

  * `date` (datetime)
  * `symbol` (string)
  * `open`, `high`, `low`, `close` (float)
  * `volume` (float)

---

### 2. Commodities (`commodities.parquet`)

* **Coverage**: Commodity ETFs (Gold, Oil, Silver, Broad commodities)
* **Columns**: Same OHLCV structure as stocks

---

### 3. Bonds (`bonds.parquet`)

* **Coverage**: Treasury and corporate bond yields
* **Columns**:

  * `date` (datetime)
  * `series` (string)
  * `value` (float)

---

### 4. Forex (`forex.parquet`)

* **Coverage**: Major currency pairs (EUR/USD, USD/JPY, etc.)
* **Columns**: Same OHLCV structure as stocks

---

### 5. Cryptocurrencies (`crypto.parquet`)

* **Coverage**: Major assets (BTC, ETH, BNB, XRP, ADA)
* **Columns**: Same OHLCV structure as stocks

---

### 6. Real Estate (`real_estate.parquet`)

* **Coverage**: Real estate ETFs (VNQ, IYR, SCHH, etc.)
* **Columns**: Same OHLCV structure as stocks

---

### 7. Resume Tracker (`resume_tracker.json`)

Tracks the last fetched state for each data source.

* `last_fetch_date`: last collection date
* `symbols` / `series`: tracked assets

---

## Logging & Reports

### Logs

* `logs/collection_log.txt`: execution logs
* `logs/error_log.txt`: error tracking

### Reports

* `reports/collection_report_YYYYMMDD.txt`: daily collection summary

---

## License

This project is licensed under the MIT License.

```
