import streamlit as st
from huggingface_hub import InferenceClient
from huggingface_hub.utils import HfHubHTTPError




MODEL = "openai/gpt-oss-20b:deepinfra"
API_TOKEN = st.secrets["hugging_face_token"]
# hugging face との接続を行うクライアントクラス
client = InferenceClient(MODEL, token=API_TOKEN)


# システムメッセージ
system_message_init = """
# 役割
あなたはユーザー専属のお笑い芸人・クイズ司会者です。
テンポの良いトークと親しみやすいツッコミで、ユーザーを楽しませることを目指します。


# タスク
お題（ジャンルやテーマ）に沿った「なぞかけ」「大喜利」「クイズ形式のギャグ」を出題し、
ユーザーの回答に対して、面白さや発想力を評価してリアクションする。


# 制約
出題は100文字程度で出力してください。
毎回、なぞかけ・大喜利（お題に対する回答）・クイズ形式（三択など）のいずれかをランダムに切り替えて出題してください。
難しい言葉や専門用語は使わず、誰でも笑える日常的な言葉で構成してください。
ユーザーのプロフィール（好きなお笑いのジャンルや性格など）を考慮して、ノリや言葉遣いを調整してください。
ユーザーの回答に対しては、必ず「良いところ」を一つは褒めてから、芸人らしい軽いツッコミを入れてください。
説教くさい解説や真面目な訂正は避け、常に明るいテンションを保ってください。


# 出力形式の例


## お題を出す例（なぞかけ）
それでは一発、なぞかけいきます！
「～～～～」とかけまして「～～～～」と解きます。
その心は……？


## お題を出す例（大喜利）
【お題】～～～～な理由を教えてください。
自由に答えてね！


## お題を出す例（三択クイズ）
【クイズ】～～～～？
A：
B：
C：


## ユーザーの回答に対するリアクション例
おお～、「～～～～」ってところ、発想がいいですね！
でも～～～～な感じもあって、そこがちょっと面白い（笑）
【点数】〇〇点／100点
それじゃあ次のお題いきますよ～！
"""
# system_message_init = """
# # 役割
# あなたはユーザー専属の家庭教師です。
# ユーザーの質問に対して、なるべく日常的な例を交えて簡単に解説をして、
# 納得できる回答をすることを目指します。


# # タスク
# 技術的な質問に対して回答を行い、ユーザーが理解したかどうかを確認する。


# # 制約
# 解説は200文字程度で出力してください。
# ポイントは2～5個程度で出力してください。
# クイズ問題は選択問題、穴埋め問題、記述問題を話題に合わせて切り替えて使用してください。
# 専門用語を使用するのはなるべく避けて、日常的な言葉だけで構成してください。
# ユーザーのプロフィールを考慮して、解説や問題の表現方法、言葉遣いを調整してください。


# # 出力形式の例


# ## 質問に対する回答の例
# ～～～～とは、一言で説明すると～～～～です。
# 身近な例では、～～～～。
# 重要なポイントは以下です。
# - ポイント1：～～～～
# - ポイント2：～～～～
# - ポイント3：～～～～


# それでは、簡単なクイズで理解できたかどうか試してみますね。
# 【問題】～～～～？


# ## クイズの例


# ### 選択問題
# ～～～～を選んでください。
# A：
# B：
# C：
# D：


# ### 穴埋め問題
# 次の空欄を埋めてください。
# ～～～～「　　　　」～～～～。


# ### 記述問題
# ～～～～？


# ## クイズの答えに対する回答の例
# 【正解】～～～～。
# あなたの回答は～～～～でしたので、結果は[正解です！／不正解です・・・。]
# [不正解の場合はさらに詳しい解説を行い、クイズを出題]
# [正解の場合]
# さらに難しいクイズに挑戦しますか？それとも他に質問したい事がありますか？
# """


description = """
このアプリケーションは、技術的な疑問を解消して、理解につなげるためのチャットアプリです。
AIに技術的な質問をすると、その解説とクイズによる理解度の確認を行います。
"""


attribute_asking = """
まずは、あなたがどのような人なのか説明してください。
職業や好きなことなど、回答を調整するための情報を入力してください。
"""


initial_conversation = [
    {"role": "assistant", "content": description},
    {"role": "assistant", "content": attribute_asking},
]




st.title("技術の相談アプリ")
st.markdown("AIに技術のことを聞いてみてください。クイズも出してくれます。")




# セッションの初期化
if "log" not in st.session_state:
    st.session_state["log"] = [
        {"role": "system", "content": system_message_init}
    ] + initial_conversation


if "profile" not in st.session_state:
    st.session_state["profile"] = None




# 会話ログを表示
for post in st.session_state["log"]:
    if post["role"] != "system":
        with st.chat_message(post["role"]):
            st.write(post["content"])




# プロフィール登録前後で入力欄を切り替える
if st.session_state["profile"] is None:
    input_placeholder = "あなた自身がどういう人か説明してください"
else:
    input_placeholder = "技術的な質問やクイズの回答を入力してください"




message = st.chat_input(input_placeholder)


if message:
    # 1回目の入力：プロフィールとして登録
    if st.session_state["profile"] is None:
        st.session_state["profile"] = message
        # システムメッセージにプロフィールを追加
        st.session_state["log"][0]["content"] = (
            system_message_init
            + "\n\n# ユーザープロフィール\n"
            + message
        )
        # プロフィールも会話ログに残す
        st.session_state["log"].append(
            {
                "role": "user",
                "content": f"私のプロフィールは次のとおりです。\n{message}",
            }
        )
        profile_reply = (
            "プロフィールを登録しました。"
            "次の入力から、技術的な質問やクイズへの回答を入力してください。"
        )
        st.session_state["log"].append(
            {"role": "assistant", "content": profile_reply}
        )
        # 状態更新後に画面全体を再実行
        st.rerun()
    # 2回目以降の入力：通常のチャット
    else:
        st.session_state["log"].append(
            {"role": "user", "content": message}
        )
        try:
            # チャット送信と返信の取得
            completion = client.chat.completions.create(
                messages=st.session_state["log"],
                max_tokens=500,
            )
            reply = completion.choices[0].message.content
            # オフラインテスト用コード、上の5行をコメントアウトして↓のコードを代わりに実行
            # reply = "これはテスト返信です"
            st.session_state["log"].append(
                {"role": "assistant", "content": reply}
            )
            st.rerun()
        except HfHubHTTPError as e:
            print(e)
            st.warning(
                "⚠️ モデルが大忙しのようです。"
                "しばらくしてからもう一度試してください。"
            )
