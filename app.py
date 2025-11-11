import streamlit as st
import requests
import math
import pandas as pd
import plotly.graph_objects as go

# 外部APIのURL
HIGHLOW_API = "https://app.kumagai-stock.com/api/highlow"
CANDLE_API = "https://app.kumagai-stock.com/api/candle"

# ページ設定
st.set_page_config(page_title="ルール1 株価チェック", layout="centered")

# CSS（入力欄の文字拡大）
st.markdown("""
    <style>
    input[type="number"], input[type="text"] {
        font-size: 22px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# タイトル
st.markdown("""
    <h1 style='text-align:left; color:#2E86C1; font-size:26px; line-height:1.4em;'>
        『ルール1』<br>株価チェックアプリ
    </h1>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("<h4>📌 <strong>注意事項</strong></h4>", unsafe_allow_html=True)

st.markdown("""
<div style='color:red; font-size:14px;'>
<ul>
    <li>このアプリは東京証券取引所（.T）上場企業のみに対応しています。</li>
    <li>平日8時30分～9時に5分程度のメンテナンスが入ることがあります。</li>
    <li>ゴールデンウィークなどの連休・イレギュラーな日程には正確に対応できない場合があります。</li>
    <li>株式分割や株式併合などがあった場合、過去の株価は分割・併合を考慮しておりません。</li>
</ul>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.caption("ルール１に該当する企業コードをこちらにご入力ください。")

# --- URLパラメータ処理 ---
query_code = st.query_params.get("code", "")
if isinstance(query_code, list):
    query_code = query_code[0]  # リストなら1つだけ取り出す
default_code = query_code if query_code else "7203"

# --- 企業コードの入力 ---
code = st.text_input("企業コード（半角英数字のみ、例: 7203）", value=default_code)

# 入力値のバリデーション
if not code or not code.isalnum():
    st.warning("正しい企業コードを入力してください（例：7203）")
    st.stop()

# --- キャッシュ化されたAPI呼び出し関数 ---

@st.cache_data(ttl=3600) # 1時間キャッシュ (高値/安値データは頻繁に更新されないため)
def get_highlow_data_cached(code):
    """高値/安値データと企業名を取得"""
    try:
        url = f"{HIGHLOW_API}/{code}" # APIの形式が変更された可能性を考慮してコードをパスに追加
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return res.json()
    except requests.RequestException:
        # 元のコードのロジックに合わせて、コードをクエリパラメータとして試行
        try:
            res = requests.get(HIGHLOW_API, params={"code": code}, timeout=10)
            res.raise_for_status()
            return res.json()
        except requests.RequestException as e:
            st.error(f"高値/安値データの取得に失敗しました: {e}")
            return None

# 🌟 チャートデータのキャッシュ時間を10分 (600秒) に短縮
@st.cache_data(ttl=600) 
def get_candle_data_cached(code):
    """ローソク足チャートデータを取得"""
    try:
        res = requests.get(CANDLE_API, params={"code": code}, timeout=10)
        res.raise_for_status()
        return res.json().get("data", [])
    except requests.RequestException as e:
        st.error(f"チャートデータの取得に失敗しました: {e}")
        return []

# --- ヘルパー関数 ---
def green_box(label, value, unit):
    st.markdown(f"""
        <div style="
            background-color: #f0fdf4;
            border-left: 4px solid #4CAF50;
            padding: 10px 15px;
            border-radius: 5px;
            margin-bottom: 10px;">
            ✅ <strong>{label}：</strong><br>
            <span style="font-size:24px; font-weight:bold;">{value} {unit}</span>
        </div>
    """, unsafe_allow_html=True)


# --- メイン処理 ---
recent_high = None
recent_low = None

if code:
    # 1. 高値・安値データの取得 (キャッシュを利用)
    highlow_data = get_highlow_data_cached(code)
    
    if highlow_data:
        try:
            company_name = highlow_data.get("name", "企業名不明")
            # データをfloatに変換して、計算ツールの入力値として使用できるように準備
            recent_high = float(highlow_data["high"])
            high_date = highlow_data["high_date"]
            recent_low = float(highlow_data["low"])
            low_date = highlow_data["low_date"]

            st.subheader(f"{company_name}（{code}）の株価情報")
            st.markdown(f"✅ **直近5営業日の高値**:<br><span style='font-size:24px'>{recent_high:.2f} 円（{high_date}）</span>", unsafe_allow_html=True)
            st.markdown(f"✅ **高値日から過去2週間以内の安値**:<br><span style='font-size:24px'>{recent_low:.2f} 円（{low_date}）</span>", unsafe_allow_html=True)

        except (KeyError, ValueError) as e:
            st.error(f"取得したデータの形式が不正です。キーまたは値を確認してください。詳細: {e}")
    else:
        st.error(f"企業コード {code} の高値/安値データが見つかりませんでした。")
        st.stop() # データがない場合は以降の処理を停止

st.markdown("---")
st.markdown("<h4>📌 <strong>注意事項</strong></h4>", unsafe_allow_html=True)

st.markdown("""
<div style='color:red; font-size:14px;'>
<ul>
    <li>チャートは当日分は反映しておりません。
</ul>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- チャート表示 ---
if code.strip():
    with st.spinner("チャートデータを取得中..."):
        # 2. チャートデータの取得 (キャッシュを利用)
        chart_data = get_candle_data_cached(code)

        if not chart_data:
            st.warning("チャートデータが取得できませんでした。")
        else:
            try:
                df = pd.DataFrame(chart_data)
                df["date"] = pd.to_datetime(df["date"], errors="coerce")
                df["date_str"] = df["date"].dt.strftime("%Y-%m-%d")

                df["hovertext"] = (
                    "日付: " + df["date_str"] + "<br>" +
                    "始値: " + df["open"].astype(str) + "<br>" +
                    "高値: " + df["high"].astype(str) + "<br>" +
                    "安値: " + df["low"].astype(str) + "<br>" +
                    "終値: " + df["close"].astype(str)
                )

                fig = go.Figure(data=[
                    go.Candlestick(
                        x=df["date_str"],
                        open=df["open"],
                        high=df["high"],
                        low=df["low"],
                        close=df["close"],
                        increasing_line_color='red',
                        decreasing_line_color='blue',
                        hovertext=df["hovertext"],
                        hoverinfo="text"
                    )
                ])

                fig.update_layout(
                    title=f"{highlow_data.get('name', '')} の3ヵ月ローソク足チャート",
                    dragmode=False,
                    xaxis_title="日付",
                    yaxis_title="株価",
                    xaxis_rangeslider_visible=False,
                    xaxis=dict(
                        type='category',
                        tickangle=-45,
                        fixedrange=True
                    ),
                    yaxis=dict(
                        fixedrange=True
                    )
                )

                st.plotly_chart(fig, use_container_width=True, config={
                    "displayModeBar": False,
                    "staticPlot": False
                })
            except Exception as e:
                st.error(f"チャート描画中にエラーが発生しました: {e}")

st.markdown("---")

# --- 計算ツール ---
if recent_high and recent_low:
    st.markdown("""
        <h2 style='text-align:left; color:#2E86C1; font-size:26px; line-height:1.4em;'>
            上げ幅の半値押し<br>計算ツール
        </h2>
    """, unsafe_allow_html=True)

    # high_inputとlow_inputにfloat型を渡す
    high_input = st.number_input("高値（円）", min_value=0.0, value=recent_high, format="%.2f")
    low_input = st.number_input("2週間以内の最安値（円）", min_value=0.0, value=recent_low, format="%.2f")
    st.caption("必要であれば高値・安値を修正して「計算する」をタップしてください。")

    if st.button("計算する"):
        if high_input > low_input > 0:
            rise_rate = high_input / low_input
            width = high_input - low_input
            half = math.floor(width / 2)
            retrace = math.floor(high_input - half) # 整数に切り下げ

            green_box("上昇率", f"{rise_rate:.2f}", "倍")
            green_box("上げ幅", f"{width:.2f}", "円")
            green_box("上げ幅の半値", f"{half}", "円")
            green_box("上げ幅の半値押し", f"{retrace}", "円")

            r_pointer_url = f"https://kzntk68d.autosns.app/cp/Rn8gETVMcu?price={retrace}"

            st.markdown(
                f"""
                <a href="{r_pointer_url}" target="_blank"
                    style="
                        display:inline-block;
                        background-color:#2E86C1;
                        color:white;
                        padding:10px 20px;
                        text-decoration:none;
                        border-radius:5px;
                        font-size:18px;
                        font-weight:bold;
                        margin-top:10px;
                    ">
                    Rポインターで指値算出する
                </a>
                """,
                unsafe_allow_html=True
            )
        else:
            st.warning("高値＞安値 の数値を正しく入力してください。")

st.markdown("---")
st.markdown("<h4>📌 <strong>注意事項</strong></h4>", unsafe_allow_html=True)


st.markdown("""
<div style='color:red; font-size:14px;'>
<ul>
    <li>ピックアップチャートの銘柄については、あくまで「ルール1」銘柄のレッスンとなります。</li>
    <li>特定の取引を推奨するものではなく、銘柄の助言ではございません。</li>
    <li>本サービスは利益を保証するものではなく、投資にはリスクが伴います。投資の際は自己責任でよろしくお願いいたします。</li>
</ul>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("""
<div style='
    text-align: center;
    color: gray;
    font-size: 14px;
    font-family: "Segoe UI", "Helvetica Neue", "Arial", sans-serif !important;
    letter-spacing: 0.5px;
    unicode-bidi: plaintext;
'>
&copy; 2025 KumagaiNext All rights reserved.
</div>
""", unsafe_allow_html=True)