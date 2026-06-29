import streamlit as st
import pickle
import pandas as pd


MODEL_PATH = "./assets/models.pkl"




# 学習済みモデルの読み込みとキャッシュ関数
@st.cache_resource
def load_model():
    with open(MODEL_PATH,"rb") as f:
        model = pickle.load(f)
    return model




# 予測実行フラグの定義
if "done" not in st.session_state:
    st.session_state["done"] = False




# 予測実行フラグの変更のための関数
def toggle_done(value=True):
    st.session_state["done"] = value




# 予測結果の取得
def estimate(table):
    df = pd.DataFrame(table)
    return 10 ** model.predict(trans.transform(df))






# 表題
st.markdown("# 東京都不動産価格の見積もり")


# モデルの読み込み
load_state = st.markdown("学習済みモデルの読み込み中...")
models = load_model()
trans = models["trans"]
model = models["model"]
load_state.markdown("")


# モデルに入力する変数をユーザー入力から取得
with st.form("入力"):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        from_station = st.selectbox(
            "駅からの時間",
            [
                '0〜4分', '5〜9分', '10〜19分', '20〜29分',
                '30分～60分', '1H～1H30', '1H30～2H', '2H～'
            ]
        )
    with col2:
        city = st.selectbox(
            "市区町村（離島を除く）",
            [
                '千代田区',
                '中央区',
                '港区',
                '新宿区',
                '文京区',
                '台東区',
                '墨田区',
                '江東区',
                '品川区',
                '目黒区',
                '大田区',
                '世田谷区',
                '渋谷区',
                '中野区',
                '杉並区',
                '豊島区',
                '北区',
                '荒川区',
                '板橋区',
                '練馬区',
                '足立区',
                '葛飾区',
                '江戸川区',
                '八王子市',
                '立川市',
                '武蔵野市',
                '三鷹市',
                '青梅市',
                '府中市',
                '昭島市',
                '調布市',
                '町田市',
                '小金井市',
                '小平市',
                '日野市',
                '東村山市',
                '国分寺市',
                '国立市',
                '福生市',
                '狛江市',
                '東大和市',
                '清瀬市',
             '東久留米市',
             '武蔵村山市',
             '多摩市',
             '稲城市',
             '羽村市',
             'あきる野市',
             '西東京市',
             '西多摩郡',
            ]
        )
    with col3:
        road = st.radio(
            "前面道路",
            ['幹線道路', '生活道路']
        )
    # 予測実行ボタン
    st.form_submit_button("決定", on_click=toggle_done, args=[True])


if st.session_state["done"]:
    # 入力された説明変数の構造化
    record = {
        "from_station": from_station,
        "city": city,
        "road": road
    }
    table = [record]
    # 予測結果の取得
    prediction = int(estimate(table)[0])
    st.metric("価格相場", f"{prediction:,} 円 / ㎡")


