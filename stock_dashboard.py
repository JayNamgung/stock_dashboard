import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 데이터 다운로드 함수
def download_stock_data(symbol, years=5):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * years)
    
    # 주가 데이터 다운로드
    stock_data = yf.download(symbol, start=start_date, end=end_date)
    
    # 재무제표 데이터 다운로드
    stock = yf.Ticker(symbol)
    income_statement = stock.financials
    balance_sheet = stock.balance_sheet
    cash_flow = stock.cashflow
    
    # 디버깅 정보 출력
    st.write(f"주가 데이터 shape: {stock_data.shape}")
    st.write(f"손익계산서 shape: {income_statement.shape}")
    st.write(f"재무상태표 shape: {balance_sheet.shape}")
    st.write(f"현금흐름표 shape: {cash_flow.shape}")
    
    # 추가 디버깅: info() 메소드 사용
    st.write("주식 정보:")
    info = stock.info
    st.json(info)
    
    return stock_data, income_statement, balance_sheet, cash_flow

# yfinance 버전 확인
st.write(f"yfinance 버전: {yf.__version__}")

# 안전하게 재무 데이터를 가져오는 함수
def safe_get_financial_data(dataframe, key):
    possible_keys = [key, key.lower(), key.upper(), key.replace(' ', '')]
    for possible_key in possible_keys:
        if possible_key in dataframe.index:
            return dataframe.loc[possible_key]
    return pd.Series(dtype='float64')  # 빈 Series 반환

# Streamlit 앱
st.title("주식 데이터 및 재무제표 대시보드")

# 주식 심볼 입력
symbol = st.text_input("주식 심볼을 입력하세요 (예: AAPL)", "AAPL")

if st.button("데이터 분석"):
    with st.spinner('데이터를 다운로드 중입니다...'):
        stock_data, income_statement, balance_sheet, cash_flow = download_stock_data(symbol)
    st.success('데이터 다운로드 완료!')

    # 주가 차트
    st.subheader("5년 주가 차트")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=stock_data.index,
                    open=stock_data['Open'],
                    high=stock_data['High'],
                    low=stock_data['Low'],
                    close=stock_data['Close'],
                    name='캔들스틱'))
    fig.update_layout(xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # 거래량 차트
    st.subheader("거래량")
    volume_chart = go.Figure()
    volume_chart.add_trace(go.Bar(x=stock_data.index, y=stock_data['Volume'], name='거래량'))
    st.plotly_chart(volume_chart, use_container_width=True)
    
    # 재무제표
    st.subheader("재무제표")
    statement_option = st.selectbox(
        "재무제표 선택",
        ("손익계산서", "재무상태표", "현금흐름표"),
        key="statement_select"
    )
    
    if statement_option == "손익계산서":
        st.dataframe(income_statement)
    elif statement_option == "재무상태표":
        st.dataframe(balance_sheet)
    else:
        st.dataframe(cash_flow)
    
    # 주요 재무 지표 시각화
    st.subheader("주요 재무 지표")
    metric_option = st.selectbox(
        "지표 선택",
        ("매출", "순이익", "영업이익"),
        key="metric_select"
    )
    
    # 재무 지표 데이터 가져오기 (에러 처리 추가)
    if metric_option == "매출":
        metric_data = safe_get_financial_data(income_statement, 'Total Revenue')
    elif metric_option == "순이익":
        metric_data = safe_get_financial_data(income_statement, 'Net Income')
    else:
        metric_data = safe_get_financial_data(income_statement, 'Operating Income')
    
    if not metric_data.empty:
        metric_chart = go.Figure()
        metric_chart.add_trace(go.Bar(x=metric_data.index, y=metric_data.values, name=metric_option))
        st.plotly_chart(metric_chart, use_container_width=True)
    else:
        st.warning(f"{metric_option} 데이터를 찾을 수 없습니다.")
    
    # 기본 통계
    st.subheader("기본 통계")
    stats = pd.DataFrame({
        '시작 가격': [stock_data['Open'].iloc[0]],
        '현재 가격': [stock_data['Close'].iloc[-1]],
        '5년 최고가': [stock_data['High'].max()],
        '5년 최저가': [stock_data['Low'].min()],
        '평균 거래량': [stock_data['Volume'].mean()],
        '최근 매출': [safe_get_financial_data(income_statement, 'Total Revenue').iloc[-1] if not safe_get_financial_data(income_statement, 'Total Revenue').empty else None],
        '최근 순이익': [safe_get_financial_data(income_statement, 'Net Income').iloc[-1] if not safe_get_financial_data(income_statement, 'Net Income').empty else None]
    })
    st.table(stats)

    # 재무제표 데이터 구조 확인을 위한 출력
    st.subheader("재무제표 구조")
    st.write("손익계산서 항목:", income_statement.index.tolist())
    st.write("재무상태표 항목:", balance_sheet.index.tolist())
    st.write("현금흐름표 항목:", cash_flow.index.tolist())

st.info("이 애플리케이션은 인터넷 연결이 필요합니다. 실시간 데이터를 사용하여 분석합니다.")