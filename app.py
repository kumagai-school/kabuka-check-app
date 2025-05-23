import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

# ページ設定（スマホ向け）
st.set_page_config(page_title="ルール1 株価チェック", layout="centered")

# CSS：タイトルのみ中央揃え、他は左寄せ＋フォント調整
st.markdown("""
    <style>
        h1.title {
            text-align: center;
            font-size: 30px;
            color: #2E86C1;
        }
        .stTextInput > div > div > input {
            font-size: 18px;
        }
        .stSubheader {
            font-size: 22px !important;
        }
        .result {
            font-size: 18px;
            margin: 10px 0;
        }
        .note {
            font-size: 14px;
            color: gray;
        }
    </style>
""", unsafe_allow_html=True)

# タイトル（中央揃え）
st.markdown("<h1 class='title'>『ルール1』<br>株価チェックアプリ</h1>", unsafe_allow_html=True)
st.caption("※このアプリは東京証券取引所（.T）上場企業のみに対応しています。")

# 入力欄
code = st.text_input("企業コード（半角英数字のみ、例: 7203）", "7203")

if code:
    ticker = code + ".T"
    end_date = datetime.today()
    start_date = end_date - timedelta(days=30)

    try:
        df = yf.download(ticker, start=start_date, end=end_date)
        stock_info = yf.Ticker(ticker).info
        company_name = stock_info.get("longName", "Company name not found")

        if not df.empty:
            recent_data = df.tail(5)
            recent_high = float(recent_data['High'].max())
            high_date = recent_data['High'].idxmax()
            if isinstance(high_date, pd.Series):
                high_date = high_date.iloc[0]
            high_date_str = high_date.strftime('%Y-%m-%d')

            start_low = high_date - timedelta(days=14)
            end_low = high_date
            low_range_data = df[(df.index >= start_low) & (df.index <= end_low)]

            if not low_range_data.empty:
                recent_low = float(low_range_data['Low'].min())
                low_date = low_range_data['Low'].idxmin()
                if isinstance(low_date, pd.Series):
                    low_date = low_date.iloc[0]
                low_date_str = low_date.strftime('%Y-%m-%d')
                low_info = f"{recent_low:.2f} 円（{low_date_str}）"
            else:
                low_info = "該当期間に安値データが見つかりませんでした"

            st.subheader(f"{company_name}（{code}）の株価情報")
            st.markdown(f"<div class='result'>✅直近5営業日の高値:<br>  {recent_high:.2f} 円（{high_date_str}）</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='result'>✅高値日から過去2週間以内の安値:<br>  {low_info}</div>", unsafe_allow_html=True)
        else:
            st.error("株価データが見つかりません。企業コードを確認してください。")

    except Exception as e:
        st.error(f"データ取得中にエラーが発生しました: {e}")

# 注意事項
st.markdown("---")
st.markdown("<div class='note'>📌 <strong>注意事項</strong><br>・このアプリは東京証券取引所（.T）上場企業のみに対応しています。<br>・ゴールデンウィークなどの連休・イレギュラーな日程には正確に対応できない場合があります。<br>・企業名はYahoo!financeから取得しており、英語表示となります。ご了承ください。</div>", unsafe_allow_html=True)
