from datetime import date
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from app.config import get_settings  # noqa: E402
from database.demo_data import seed_demo_dataset  # noqa: E402
from database.export import (  # noqa: E402
    daily_features_frame,
    dataframe_to_csv_bytes,
    dataframe_to_json_bytes,
    listed_stocks_frame,
    news_raw_frame,
)
from database.repositories.predictions import PredictionsRepository  # noqa: E402
from database.session import SessionLocal, init_db  # noqa: E402
from models.run_prediction import train_predict_and_store  # noqa: E402
from models.stock_signal import analyze_company_by_name  # noqa: E402

st.set_page_config(page_title="국내 뉴스 기반 시장 예측", layout="wide")
init_db()

st.title("기업 뉴스 기반 상승/하락 가능성 분석")
st.caption("기업명을 입력하면 상장 종목 정보, 관련 뉴스 수집, 뉴스 신호 기반 확률 예측을 실행합니다.")

settings = get_settings()


def run_index_model() -> None:
    with SessionLocal() as db:
        train_predict_and_store(db)


def seed_demo_data() -> dict[str, int]:
    with SessionLocal() as db:
        return seed_demo_dataset(db)


def analyze_company(company_name: str) -> dict:
    with SessionLocal() as db:
        result = analyze_company_by_name(db, company_name)
        return {
            "target_symbol": result.target_symbol,
            "item_name": result.item_name,
            "news_count": result.news_count,
            "prob_up": result.prob_up,
            "confidence": result.confidence,
            "top_news": result.top_news,
        }


def load_predictions() -> list:
    try:
        with SessionLocal() as db:
            return PredictionsRepository(db).latest(limit=30)
    except Exception as exc:
        st.warning(f"예측 결과를 불러올 수 없습니다: {exc}")
        return []


def load_export_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    try:
        with SessionLocal() as db:
            return news_raw_frame(db), daily_features_frame(db), listed_stocks_frame(db)
    except Exception as exc:
        st.warning(f"분석 데이터를 불러올 수 없습니다: {exc}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


def company_suggestions(stock_frame: pd.DataFrame, query: str) -> list[str]:
    fallback = ["삼성전자", "SK하이닉스", "현대차", "NAVER", "카카오", "LG에너지솔루션"]
    if stock_frame.empty or "item_name" not in stock_frame.columns:
        return fallback

    names = (
        stock_frame["item_name"]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .sort_values()
        .tolist()
    )
    if query.strip():
        lowered = query.strip().lower()
        matched = [name for name in names if lowered in name.lower()]
    else:
        matched = names

    suggestions = matched[:20]
    for name in fallback:
        if name not in suggestions:
            suggestions.append(name)
    return suggestions[:30]


with st.sidebar:
    st.header("설정")
    st.caption(f"실행 환경: {settings.app_env}")
    st.caption(f"데이터베이스: {settings.database_url}")
    st.caption("공공데이터 인증키는 .env의 PUBLIC_DATA_SERVICE_KEY를 사용합니다.")
    if st.button("지수 예측 새로고침", use_container_width=True):
        try:
            with st.spinner("지수 예측 모델을 학습하고 있습니다..."):
                run_index_model()
            st.success("지수 예측을 갱신했습니다.")
            st.rerun()
        except Exception as exc:
            st.error(f"지수 예측 실패: {exc}")
    if st.button("시연 데이터 생성", use_container_width=True):
        try:
            inserted = seed_demo_data()
            st.success(
                f"feature {inserted['daily_features']}건, 뉴스 {inserted['news_raw']}건을 생성했습니다."
            )
            st.rerun()
        except Exception as exc:
            st.error(f"시연 데이터 생성 실패: {exc}")

predictions = load_predictions()
news_frame, feature_frame, stock_frame = load_export_frames()

suggestions = company_suggestions(stock_frame, "")
company_name = st.selectbox(
    "기업명 검색",
    options=suggestions,
    index=None,
    placeholder="예: 삼성전자, SK하이닉스, 현대차",
    accept_new_options=True,
    filter_mode="fuzzy",
    help="기업명을 입력하면 추천 기업이 자동으로 필터링됩니다. 목록에 없으면 입력한 기업명을 그대로 사용합니다.",
)

if st.button("기업 분석 실행", type="primary", use_container_width=True):
    if not company_name or not company_name.strip():
        st.warning("기업명을 입력해주세요.")
    elif not settings.public_data_service_key:
        st.error(".env에 PUBLIC_DATA_SERVICE_KEY가 설정되어 있지 않습니다.")
    else:
        try:
            with st.spinner("상장 종목 정보 조회, 뉴스 수집, 상승/하락 신호 계산을 실행 중입니다..."):
                signal = analyze_company(company_name.strip())
            st.success(
                f"{signal['target_symbol']} 분석 완료: "
                f"상승 가능성 {signal['prob_up'] * 100:.1f}%, "
                f"신뢰도 {signal['confidence'] * 100:.1f}%"
            )
            st.session_state["last_company_signal"] = signal
            st.rerun()
        except Exception as exc:
            st.error(f"기업 분석 실패: {exc}")

last_signal = st.session_state.get("last_company_signal")
if last_signal:
    col1, col2, col3 = st.columns(3)
    col1.metric("분석 대상", last_signal["target_symbol"])
    col2.metric("상승 가능성", f"{last_signal['prob_up'] * 100:.1f}%")
    col3.metric("분석 뉴스 수", f"{last_signal['news_count']}건")

    with st.expander("관련 뉴스", expanded=True):
        top_news = pd.DataFrame(last_signal["top_news"])
        if top_news.empty:
            st.info("관련 뉴스가 아직 없습니다.")
        else:
            st.dataframe(top_news, use_container_width=True, hide_index=True)

st.subheader("최근 예측 결과")
if predictions:
    rows = []
    for prediction in predictions:
        explanation = prediction.explanation or {}
        rows.append(
            {
                "날짜": prediction.prediction_date,
                "대상": prediction.target_symbol,
                "기간": prediction.horizon,
                "상승확률": round(float(prediction.prob_up) * 100, 2),
                "신뢰도": round(float(prediction.confidence or 0) * 100, 2),
                "모델": explanation.get("model_name", "unknown"),
                "생성시각": prediction.created_at,
            }
        )
    result_frame = pd.DataFrame(rows)
    st.dataframe(result_frame, use_container_width=True, hide_index=True)

    chart_frame = result_frame.rename(columns={"날짜": "date", "상승확률": "prob_up", "대상": "symbol"})
    chart_frame["date"] = pd.to_datetime(
        chart_frame["date"].astype(str).where(chart_frame["date"].notna(), str(date.today()))
    )
    st.line_chart(chart_frame, x="date", y="prob_up", color="symbol")
else:
    st.info("아직 저장된 예측 결과가 없습니다. 기업명을 입력하고 기업 분석 실행을 눌러주세요.")

with st.expander("수집 데이터 내려받기", expanded=False):
    c1, c2, c3 = st.columns(3)
    c1.metric("뉴스 원문", len(news_frame))
    c2.metric("상장 종목", len(stock_frame))
    c3.metric("feature", len(feature_frame))

    d1, d2, d3 = st.columns(3)
    d1.download_button(
        "뉴스 CSV 받기",
        data=dataframe_to_csv_bytes(news_frame),
        file_name="scraped_news_raw.csv",
        mime="text/csv",
        use_container_width=True,
        disabled=news_frame.empty,
    )
    d2.download_button(
        "뉴스 JSON 받기",
        data=dataframe_to_json_bytes(news_frame),
        file_name="scraped_news_raw.json",
        mime="application/json",
        use_container_width=True,
        disabled=news_frame.empty,
    )
    d3.download_button(
        "상장 종목 CSV 받기",
        data=dataframe_to_csv_bytes(stock_frame),
        file_name="listed_stocks.csv",
        mime="text/csv",
        use_container_width=True,
        disabled=stock_frame.empty,
    )

    st.write("뉴스 미리보기")
    if news_frame.empty:
        st.info("수집된 뉴스가 없습니다.")
    else:
        st.dataframe(news_frame.head(50), use_container_width=True, hide_index=True)

    st.write("상장 종목 미리보기")
    if stock_frame.empty:
        st.info("수집된 상장 종목 정보가 없습니다.")
    else:
        st.dataframe(stock_frame.head(50), use_container_width=True, hide_index=True)

st.caption("본 결과는 연구 목적의 확률 예측이며, 투자자문이나 매수/매도 추천이 아닙니다.")
