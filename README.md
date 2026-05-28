# Korea News Market Predictor

국내 뉴스, 공시, 거시지표, 시장 데이터를 기반으로 KOSPI/KOSDAQ의 다음 거래일 방향성을 확률로 예측하는 리서치형 MVP입니다.

> 본 시스템은 연구 및 정보 분석 목적의 확률 예측 도구입니다. 특정 종목의 매수·매도 추천, 투자자문, 자동매매를 목적으로 하지 않습니다.

## MVP Scope

- FastAPI backend
- PostgreSQL + SQLAlchemy persistence
- Collector interfaces for Naver News, DART, ECOS, KIS/KRX, RSS
- News cleaning and deduplication primitives
- Daily feature builder with cutoff-time leakage protection
- Baseline model training interfaces
- Walk-forward backtest utilities
- Streamlit dashboard shell

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev,ml,dashboard]"
cp .env.example .env
docker compose up -d postgres pgadmin
uvicorn app.main:app --reload
```

Dashboard:

```bash
streamlit run dashboard/streamlit_app.py
```

Run model inference after `daily_features` has labeled rows:

```bash
curl -X POST http://127.0.0.1:8000/predictions/run ^
  -H "Content-Type: application/json" ^
  -d "{\"symbols\":[\"KOSPI\",\"KOSDAQ\"],\"prefer_lightgbm\":true}"
```

## Public Data Key

개별 종목 조회에는 공공데이터포털의 `금융위원회_KRX상장종목정보` serviceKey가 필요합니다.

```env
PUBLIC_DATA_SERVICE_KEY=your_service_key_here
```

대시보드에서는 키를 노출하지 않고 종목명만 입력해 조회합니다.

Tests:

```bash
pytest
```
