import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

st.markdown(
    "<h1 style='text-align: center; color: #2E86C1;'>『ルール1』<br>株価チェックアプリ</h1>",
    unsafe_allow_html=True
)

st.caption("※このアプリは東京証券取引所（.T）上場企業のみに対応しています。")


# 数字だけの企業コードを入力（例：7203）
code = st.text_input("企業コード（数字のみ、例: 7203）", "7203")

if code:
    ticker = code + ".T"
    end_date = datetime.today()
    start_date = end_date - timedelta(days=30)

    try:
        # 株価データ取得
        df = yf.download(ticker, start=start_date, end=end_date)
        stock_info = yf.Ticker(ticker).info
        company_name = stock_info.get("longName", "Company name not found")

        if not df.empty:
            # 直近5営業日の高値とその日付
            recent_data = df.tail(5)
            recent_high = float(recent_data['High'].max())
            high_date = recent_data['High'].idxmax()
            if isinstance(high_date, pd.Series):
                high_date = high_date.iloc[0]
            high_date_str = high_date.strftime('%Y-%m-%d')

            # 高値日から過去2週間分のデータを取得（高値日含む）
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

            # 表示
            st.subheader(f"{company_name}（{code}）の株価情報")
            st.write(f"✅ **直近5営業日の高値**: {recent_high:.2f} 円（{high_date_str}）")
            st.write(f"✅ **高値日から過去2週間以内の安値**: {low_info}")

        else:
            st.error("株価データが見つかりません。企業コードを確認してください。")
    except Exception as e:
        st.error(f"データ取得中にエラーが発生しました: {e}")


st.markdown("---")
st.caption("📌 **注意事項**")
st.caption("・このアプリは東京証券取引所（.T）上場企業のみに対応しています。")
st.caption("・ゴールデンウィークなどの連休・イレギュラーな日程には正確に対応できない場合があります。")

