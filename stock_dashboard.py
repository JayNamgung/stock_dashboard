import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

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
    
    return stock_data, income_statement, balance_sheet, cash_flow

# 데이터 저장 함수
def save_data(symbol, stock_data, income_statement, balance_sheet, cash_flow):
    if not os.path.exists('data'):
        os.makedirs('data')
    
    stock_data.to_csv(f"data/{symbol}_stock_data.csv")
    income_statement.to_csv(f"data/{symbol}_income_statement.csv")
    balance_sheet.to_csv(f"data/{symbol}_balance_sheet.csv")
    cash_flow.to_csv(f"data/{symbol}_cash_flow.csv")

# Streamlit 앱
st.title("주식 데이터 및 재무제표 대시보드")

# 주식 심볼 입력
symbol = st.text_input("주식 심볼을 입력하세요 (예: AAPL)", "AAPL")

# 데이터 소스 선택
data_source = st.radio("데이터 소스 선택", ("온라인 (자동 다운로드)", "오프라인 (저장된 파일 사용)"))

if data_source == "온라인 (자동 다운로드)":
    if st.button("데이터 다운로드 및 분석"):
        with st.spinner('데이터를 다운로드 중입니다...'):
            stock_data, income_statement, balance_sheet, cash_flow = download_stock_data(symbol)
            save_data(symbol, stock_data, income_statement, balance_sheet, cash_flow)
        st.success('데이터 다운로드 완료!')
else:
    stock_data_file = st.file_uploader("주가 데이터 CSV 파일을 선택하세요", type="csv")
    income_statement_file = st.file_uploader("손익계산서 CSV 파일을 선택하세요", type="csv")
    balance_sheet_file = st.file_uploader("재무상태표 CSV 파일을 선택하세요", type="csv")
    cash_flow_file = st.file_uploader("현금흐름표 CSV 파일을 선택하세요", type="csv")
    
    if stock_data_file and income_statement_file and balance_sheet_file and cash_flow_file:
        stock_data = pd.read_csv(stock_data_file, index_col=0, parse_dates=True)
        income_statement = pd.read_csv(income_statement_file, index_col=0)
        balance_sheet = pd.read_csv(balance_sheet_file, index_col=0)
        cash_flow = pd.read_csv(cash_flow_file, index_col=0)
    else:
        st.warning("모든 필요한 CSV 파일을 업로드해주세요.")
        st.stop()

# 데이터 분석 및 시각화
if 'stock_data' in locals():
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
        ("손익계산서", "재무상태표", "현금흐름표")
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
        ("매출", "순이익", "영업이익")
    )
    
    if metric_option == "매출":
        metric_data = income_statement.loc['Total Revenue']
    elif metric_option == "순이익":
        metric_data = income_statement.loc['Net Income']
    else:
        metric_data = income_statement.loc['Operating Income']
    
    metric_chart = go.Figure()
    metric_chart.add_trace(go.Bar(x=metric_data.index, y=metric_data.values, name=metric_option))
    st.plotly_chart(metric_chart, use_container_width=True)
    
    # 기본 통계
    st.subheader("기본 통계")
    stats = pd.DataFrame({
        '시작 가격': [stock_data['Open'].iloc[0]],
        '현재 가격': [stock_data['Close'].iloc[-1]],
        '5년 최고가': [stock_data['High'].max()],
        '5년 최저가': [stock_data['Low'].min()],
        '평균 거래량': [stock_data['Volume'].mean()],
        '최근 매출': [income_statement.loc['Total Revenue'].iloc[-1]],
        '최근 순이익': [income_statement.loc['Net Income'].iloc[-1]]
    })
    st.table(stats)