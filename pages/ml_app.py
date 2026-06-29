import streamlit as st
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

MODEL_PATH = "./assets/models.pkl"

@st.cache_resource
def load_model():
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    return model

if "done" not in st.session_state:
    st.session_state["done"] = False
if "comparison" not in st.session_state:
    st.session_state["comparison"] = []

def toggle_done(value=True):
    st.session_state["done"] = value

def estimate(table):
    df = pd.DataFrame(table)
    return 10 ** model.predict(trans.transform(df))

STATIONS = ['0〜4分', '5〜9分', '10〜19分', '20〜29分', '30分～60分', '1H～1H30', '1H30～2H', '2H～']
STATIONS_SHORT = ['0〜4分', '5〜9分', '10〜19分', '20〜29分', '30分～60分']
CITIES = [
    '千代田区','中央区','港区','新宿区','文京区','台東区','墨田区','江東区',
    '品川区','目黒区','大田区','世田谷区','渋谷区','中野区','杉並区','豊島区',
    '北区','荒川区','板橋区','練馬区','足立区','葛飾区','江戸川区','八王子市',
    '立川市','武蔵野市','三鷹市','青梅市','府中市','昭島市','調布市','町田市',
    '小金井市','小平市','日野市','東村山市','国分寺市','国立市','福生市','狛江市',
    '東大和市','清瀬市','東久留米市','武蔵村山市','多摩市','稲城市','羽村市',
    'あきる野市','西東京市','西多摩郡',
]

# ─────────────────────────────────────────
st.markdown("# 東京都不動産価格の見積もり")

load_state = st.markdown("学習済みモデルの読み込み中...")
models = load_model()
trans = models["trans"]
model = models["model"]
load_state.markdown("")

# ── Feature 1: Comparison Table ──────────
st.markdown("### 🔍 条件を選んで比較リストに追加")

with st.form("入力"):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        from_station = st.selectbox("駅からの時間", STATIONS)
    with col2:
        city = st.selectbox("市区町村（離島を除く）", CITIES)
    with col3:
        road = st.radio("前面道路", ['幹線道路', '生活道路'])

    col_btn1, col_btn2 = st.columns([1, 2])
    with col_btn1:
        submitted = st.form_submit_button("決定", on_click=toggle_done, args=[True])
    with col_btn2:
        add_to_compare = st.form_submit_button("＋ 比較リストに追加")

if st.session_state["done"]:
    record = {"from_station": from_station, "city": city, "road": road}
    prediction = int(estimate([record])[0])
    st.metric("価格相場", f"{prediction:,} 円 / ㎡")

if add_to_compare:
    record = {"from_station": from_station, "city": city, "road": road}
    prediction = int(estimate([record])[0])
    entry = {"市区町村": city, "駅からの時間": from_station, "前面道路": road, "価格相場 (円/㎡)": prediction}
    existing = [e for e in st.session_state["comparison"]
                if e["市区町村"] == city and e["駅からの時間"] == from_station and e["前面道路"] == road]
    if existing:
        st.warning("この条件はすでにリストにあります。")
    else:
        st.session_state["comparison"].append(entry)
        st.success(f"{city} / {from_station} / {road} を追加しました！")

if st.session_state["comparison"]:
    st.markdown("---")
    st.markdown("### 📋 比較リスト")
    df_compare = pd.DataFrame(st.session_state["comparison"])
    df_compare = df_compare.sort_values("価格相場 (円/㎡)", ascending=False).reset_index(drop=True)
    df_compare.index += 1
    df_display = df_compare.copy()
    df_display["価格相場 (円/㎡)"] = df_display["価格相場 (円/㎡)"].apply(lambda x: f"{x:,}")
    st.dataframe(df_display, use_container_width=True)

    col_dl, col_clear = st.columns([1, 4])
    with col_dl:
        csv = df_compare.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("📥 CSVダウンロード", data=csv, file_name="不動産比較.csv", mime="text/csv")
    with col_clear:
        if st.button("🗑️ リストをクリア"):
            st.session_state["comparison"] = []
            st.rerun()

# ── Feature 2: Heatmap ───────────────────
st.markdown("---")
st.markdown("### 🗺️ Heatmap: 駅距離・エリア別価格")

with st.expander("表示エリアを選択", expanded=False):
    selected_cities = st.multiselect(
        "市区町村（最大15件）",
        options=['千代田区','中央区','港区','新宿区','文京区',
                 '台東区','墨田区','江東区','品川区','目黒区',
                 '大田区','世田谷区','渋谷区','中野区','杉並区'],
        default=['千代田区','港区','新宿区','渋谷区','文京区'],
        max_selections=15
    )
    heatmap_road = st.radio("前面道路", ['幹線道路', '生活道路'], horizontal=True)

if st.button("Heatmap を生成"):
    if not selected_cities:
        st.warning("エリアを1つ以上選択してください。")
    else:
        with st.spinner("計算中..."):
            matrix = []
            for c in selected_cities:
                row = []
                for s in STATIONS_SHORT:
                    val = int(estimate([{"from_station": s, "city": c, "road": heatmap_road}])[0])
                    row.append(val)
                matrix.append(row)

        matrix_np = np.array(matrix)
        fig, ax = plt.subplots(figsize=(9, max(3, len(selected_cities) * 0.55)))
        im = ax.imshow(matrix_np, cmap="Blues", aspect="auto")
        ax.set_xticks(range(len(STATIONS_SHORT)))
        ax.set_xticklabels(STATIONS_SHORT, fontsize=9)
        ax.set_yticks(range(len(selected_cities)))
        ax.set_yticklabels(selected_cities, fontsize=9)
        plt.colorbar(im, ax=ax, label="円/㎡")

        vmin, vmax = matrix_np.min(), matrix_np.max()
        for i in range(len(selected_cities)):
            for j in range(len(STATIONS_SHORT)):
                val = matrix_np[i, j]
                color = "white" if val > (vmin + vmax) / 2 else "black"
                ax.text(j, i, f"{val:,}", ha="center", va="center", fontsize=7, color=color)

        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

# ── Feature 3: Bar Chart ─────────────────
st.markdown("---")
st.markdown("### 📊 Bar Chart: エリア別価格比較")

col_b1, col_b2, col_b3 = st.columns([2, 1, 1])
with col_b1:
    bar_cities = st.multiselect(
        "市区町村（最大10件）",
        options=['千代田区','中央区','港区','新宿区','文京区',
                 '台東区','墨田区','江東区','品川区','目黒区',
                 '大田区','世田谷区','渋谷区','中野区','杉並区',
                 '豊島区','北区','荒川区','板橋区','練馬区'],
        default=['千代田区','港区','新宿区','渋谷区','文京区'],
        max_selections=10, key="bar_cities"
    )
with col_b2:
    bar_station = st.selectbox("駅からの時間", STATIONS_SHORT, key="bar_station")
with col_b3:
    bar_road = st.radio("前面道路", ['幹線道路', '生活道路'], key="bar_road")

if st.button("Bar Chart を生成"):
    if not bar_cities:
        st.warning("エリアを1つ以上選択してください。")
    else:
        with st.spinner("計算中..."):
            prices = [int(estimate([{"from_station": bar_station, "city": c, "road": bar_road}])[0])
                      for c in bar_cities]

        sorted_pairs = sorted(zip(bar_cities, prices), key=lambda x: x[1], reverse=True)
        cities_s, prices_s = zip(*sorted_pairs)
        colors = ["#2a78d6" if p == max(prices_s) else "#b5d4f4" for p in prices_s]

        fig, ax = plt.subplots(figsize=(max(5, len(cities_s) * 0.9), 4))
        bars = ax.bar(cities_s, prices_s, color=colors, width=0.6)
        ax.set_ylabel("円/㎡")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
        ax.set_xticks(range(len(cities_s)))
        ax.set_xticklabels(cities_s, rotation=30, ha="right", fontsize=9)
        ax.spines[['top', 'right']].set_visible(False)
        for bar, p in zip(bars, prices_s):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(prices_s) * 0.01,
                    f"{p:,}", ha="center", va="bottom", fontsize=8)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        col_t1, col_t2 = st.columns(2)
        col_t1.metric("最高値", f"{max(prices_s):,} 円/㎡", cities_s[0])
        col_t2.metric("最安値", f"{min(prices_s):,} 円/㎡", cities_s[-1])

# ── Feature 4: Real-time ─────────────────
st.markdown("---")
st.markdown("### ⚡ リアルタイム見積もり")
st.caption("条件を変えると即座に更新されます")

col_r1, col_r2, col_r3 = st.columns([1, 1, 1])
with col_r1:
    rt_station = st.selectbox("駅からの時間", STATIONS, key="rt_station")
with col_r2:
    rt_city = st.selectbox("市区町村", CITIES, key="rt_city")
with col_r3:
    rt_road = st.radio("前面道路", ['幹線道路', '生活道路'], key="rt_road")

rt_price = int(estimate([{"from_station": rt_station, "city": rt_city, "road": rt_road}])[0])
st.metric("価格相場", f"{rt_price:,} 円 / ㎡")

MAX_REF = 3_000_000
st.progress(min(rt_price / MAX_REF, 1.0))
st.caption(f"参考最高値 {MAX_REF:,} 円/㎡ との比較")

# import streamlit as st
# import pickle
# import pandas as pd


# MODEL_PATH = "./assets/models.pkl"




# # 学習済みモデルの読み込みとキャッシュ関数
# @st.cache_resource
# def load_model():
#     with open(MODEL_PATH,"rb") as f:
#         model = pickle.load(f)
#     return model




# # 予測実行フラグの定義
# if "done" not in st.session_state:
#     st.session_state["done"] = False




# # 予測実行フラグの変更のための関数
# def toggle_done(value=True):
#     st.session_state["done"] = value




# # 予測結果の取得
# def estimate(table):
#     df = pd.DataFrame(table)
#     return 10 ** model.predict(trans.transform(df))






# # 表題
# st.markdown("# 東京都不動産価格の見積もり")


# # モデルの読み込み
# load_state = st.markdown("学習済みモデルの読み込み中...")
# models = load_model()
# trans = models["trans"]
# model = models["model"]
# load_state.markdown("")


# # モデルに入力する変数をユーザー入力から取得
# with st.form("入力"):
#     col1, col2, col3 = st.columns([1, 1, 1])
#     with col1:
#         from_station = st.selectbox(
#             "駅からの時間",
#             [
#                 '0〜4分', '5〜9分', '10〜19分', '20〜29分',
#                 '30分～60分', '1H～1H30', '1H30～2H', '2H～'
#             ]
#         )
#     with col2:
#         city = st.selectbox(
#             "市区町村（離島を除く）",
#             [
#                 '千代田区',
#                 '中央区',
#                 '港区',
#                 '新宿区',
#                 '文京区',
#                 '台東区',
#                 '墨田区',
#                 '江東区',
#                 '品川区',
#                 '目黒区',
#                 '大田区',
#                 '世田谷区',
#                 '渋谷区',
#                 '中野区',
#                 '杉並区',
#                 '豊島区',
#                 '北区',
#                 '荒川区',
#                 '板橋区',
#                 '練馬区',
#                 '足立区',
#                 '葛飾区',
#                 '江戸川区',
#                 '八王子市',
#                 '立川市',
#                 '武蔵野市',
#                 '三鷹市',
#                 '青梅市',
#                 '府中市',
#                 '昭島市',
#                 '調布市',
#                 '町田市',
#                 '小金井市',
#                 '小平市',
#                 '日野市',
#                 '東村山市',
#                 '国分寺市',
#                 '国立市',
#                 '福生市',
#                 '狛江市',
#                 '東大和市',
#                 '清瀬市',
#              '東久留米市',
#              '武蔵村山市',
#              '多摩市',
#              '稲城市',
#              '羽村市',
#              'あきる野市',
#              '西東京市',
#              '西多摩郡',
#             ]
#         )
#     with col3:
#         road = st.radio(
#             "前面道路",
#             ['幹線道路', '生活道路']
#         )
#     # 予測実行ボタン
#     st.form_submit_button("決定", on_click=toggle_done, args=[True])


# if st.session_state["done"]:
#     # 入力された説明変数の構造化
#     record = {
#         "from_station": from_station,
#         "city": city,
#         "road": road
#     }
#     table = [record]
#     # 予測結果の取得
#     prediction = int(estimate(table)[0])
#     st.metric("価格相場", f"{prediction:,} 円 / ㎡")


