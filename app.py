
import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import math

# ページ設定
st.set_page_config(page_title="ルール1 株価チェック", layout="centered")

# CSSで入力欄の文字サイズ拡大
st.markdown("""
    <style>
    input[type="number"] {
        font-size: 22px !important;
    }
    input[type="text"] {
        font-size: 22px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# タイトル（左寄せ・2行）
st.markdown(
    """
    <h1 style='text-align:left; color:#2E86C1; font-size:26px; line-height:1.4em;'>
        『ルール1』<br>株価チェックアプリ
    </h1>
    """,
    unsafe_allow_html=True
)

st.caption("※このアプリは東京証券取引所（.T）上場企業のみに対応しています。")

# ヘルパー関数：緑の枠＋大きな数値
def green_box(label, value, unit):
    st.markdown(f"""
    <div style="
        background-color: #f0fdf4;
        border-left: 4px solid #4CAF50;
        padding: 10px 15px;
        border-radius: 5px;
        margin-bottom: 10px;
    ">
        ✅ <strong>{label}：</strong><br>
        <span style="font-size:24px; font-weight:bold;">{value} {unit}</span>
    </div>
    """, unsafe_allow_html=True)


# 入力
code = st.text_input("企業コード（数字のみ、例: 7203）", "7203")

# 株価取得＆表示
recent_high = None
recent_low = None

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
            recent_high = float(recent_data["High"].max())

            high_date = recent_data["High"].idxmax()
            if isinstance(high_date, pd.Series):
                high_date = high_date.iloc[0]
            high_date_str = pd.to_datetime(high_date).strftime("%Y-%m-%d")

            start_low = high_date - timedelta(days=14)
            end_low = high_date
            win = df[(df.index >= start_low) & (df.index <= end_low)]

            if not win.empty:
                recent_low = float(win["Low"].min())
                low_date = win["Low"].idxmin()
                if isinstance(low_date, pd.Series):
                    low_date = low_date.iloc[0]
                low_date_str = pd.to_datetime(low_date).strftime("%Y-%m-%d")
                low_info_str = f"{recent_low:.2f} 円（{low_date_str}）"
            else:
                low_info_str = "該当期間に安値データがありません"

            st.subheader(f"{company_name}（{code}）の株価情報")

            st.markdown(f"✅ **直近5営業日の高値**:<br><span style='font-size:24px'>{recent_high:.2f} 円（{high_date_str}）</span>", unsafe_allow_html=True)
            st.markdown(f"✅ **高値日から過去2週間以内の安値**:<br><span style='font-size:24px'>{low_info_str}</span>", unsafe_allow_html=True)

        else:
            st.error("株価データが見つかりません。企業コードを確認してください。")

    except Exception as e:
        st.error(f"データ取得中にエラーが発生しました: {e}")

# 計算ツール
if recent_high is not None and recent_low is not None:
    st.markdown("---")
    st.markdown("<h2 style='text-align:left;'>ルール１<br>上げ幅の半値押し 計算ツール</h2>", unsafe_allow_html=True)

    high_input = st.number_input("高値（円）", min_value=0.0, value=recent_high, format="%.2f")
    low_input  = st.number_input("2週間以内の最安値（円）", min_value=0.0, value=recent_low, format="%.2f")

    if st.button("計算する"):
        if high_input > low_input and low_input > 0:
            rise_rate = high_input / low_input
            width     = high_input - low_input
            half      = math.floor(width / 2)
            retrace   = math.floor(high_input - half)

            green_box("上昇率", f"{rise_rate:.2f}", "倍")
            green_box("上げ幅", f"{width:.2f}", "円")
            green_box("上げ幅の半値", f"{half}", "円")
            green_box("上げ幅の半値押し", f"{retrace}", "円")


        else:
            st.warning("高値＞安値 の数値を正しく入力してください。")

st.markdown("---")
st.caption("📌 **注意事項**")
st.caption("・東証銘柄のみ対応しています。")
st.caption("・ゴールデンウィークなどの連休には対応していません。")
