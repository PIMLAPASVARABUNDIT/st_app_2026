import streamlit as st
import requests
import json

from datetime import date
from dateutil.relativedelta import relativedelta

# 関数の定義部分

## サーバー側ファイルの読み込み
def get_user_id(family_name, first_name):
    # ファイルの読み込み、パスは作業ディレクトリからの相対パス
    with open("./assets/known_people.json", "r", encoding="utf-8") as f:
        people = json.loads(f.read())
    matched = filter(
        lambda d:d["first_name"] == first_name and d["family_name"] == family_name,
        people
    )
    matched = list(matched)
    if len(matched) > 0:
        return matched[0]["id"]
    else:
        return None
    # 照合結果idを返す

## Webリソースの取得

### 名前から年齢を予測
@st.cache_data
def agify(first_name):
    url = "https://api.agify.io/"
    params = {"name": first_name}
    response = requests.get(url, params=params)
    result = json.loads(response.content)
    # resultの例 : {"count":1,"name":"伸也","age":54}
    age = result["age"]
    return age


### 名前から性別を予測
@st.cache_data
def genderize(first_name):
    url = "https://api.genderize.io/"
    params = {"name": first_name}
    response = requests.get(url, params=params)
    result = json.loads(response.content)
    # resultの例 : {"count":12,"name":"伸也","gender":"male","probability":0.93}
    gender = result["gender"]
    return gender


### 名前から国籍を予測
@st.cache_data
def nationalize(first_name):
    url = "https://api.nationalize.io/"
    params = {"name": first_name}
    response = requests.get(url, params=params)
    result = json.loads(response.content)
    # resultの例 : {"count":4,"name":"金井","country":[{"country_id":"JP","probability":0.570272},{"country_id":"HK","probability":0.429728}]}
    country = result["country"][0]["country_id"]
    return country


# 以下、表示部分
st.markdown("# プロファイル予測アプリ")

## ユーザー入力の受け取り
### 名前の入力
family_name = st.text_input("姓を入力してください。")
first_name = st.text_input("名を入力してください。")

## ユーザーへの情報表示
if st.button("入力完了"):
    ### ユーザーIDの確認
    user_id = get_user_id(family_name, first_name)
    user_id_text = f"ユーザーID: {user_id}" if user_id else "ゲスト"
    ### フルネームの計算
    full_name = family_name + first_name
    ### 予測結果の取得
    age = agify(first_name)
    gender = genderize(first_name)
    country = nationalize(first_name)
    ### 結果の表示
    st.text(f"{full_name}({user_id_text})さんの予測結果")
    st.table(
        {
            "年齢": age,
            "性別": gender,
            "国籍": country
        }
    )