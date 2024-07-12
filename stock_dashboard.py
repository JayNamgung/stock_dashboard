import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta

"""
실행 : streamlit run stock_dashboard.py
"""

# 페이지 설정
st.set_page_config(page_title="주식 가격 대시보드", layout="wide")

# 제목
st.title("주식 가격 대시보드")

# 사이드바에 주식 심볼 입력 필드 추가
stock_symbol = st.sidebar.text_input("주식 심볼 입력", value="AAPL")

# 날짜 선택
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("시작일", date.today() - timedelta(days=30))
with col2:
    end_date = st.date_input("종료일", date.today())

# 데이터 다운로드
@st.cache_data
def load_data(symbol, start, end):
    data = yf.download(symbol, start=start, end=end)
    return data

data = load_data(stock_symbol, start_date, end_date)

# 주식 차트
st.subheader(f"{stock_symbol} 주가 차트")
fig = go.Figure()
fig.add_trace(go.Candlestick(x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='캔들스틱'))
fig.update_layout(xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

# 거래량 차트
st.subheader("거래량")
volume_chart = go.Figure()
volume_chart.add_trace(go.Bar(x=data.index, y=data['Volume'], name='거래량'))
st.plotly_chart(volume_chart, use_container_width=True)

# 기본 통계
st.subheader("기본 통계")
stats = pd.DataFrame({
    '시작 가격': [data['Open'].iloc[0]],
    '종료 가격': [data['Close'].iloc[-1]],
    '최고 가격': [data['High'].max()],
    '최저 가격': [data['Low'].min()],
    '평균 거래량': [data['Volume'].mean()]
})
st.table(stats)

# 데이터 표시
st.subheader("원본 데이터")
st.dataframe(data)