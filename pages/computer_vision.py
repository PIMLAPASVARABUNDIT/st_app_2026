import json
import streamlit as st
from google.cloud import vision


# 定数の定義部分
ACCENT_COLOR = "#e5548f"
BG_SOFT = "#fdf2f7"


# Google APIキーの読み取り
credentials_dict = json.loads(st.secrets["google_credentials"], strict=False)
client = vision.ImageAnnotatorClient.from_service_account_info(info=credentials_dict)


# 関数の定義部分


# 画像処理 API とのやりとりとキャッシュ関数
@st.cache_data
def get_response(content):
    image = vision.Image(content=content)
    response = client.label_detection(image=image)

    return response


# 以下、表示部分
st.markdown(
    """
    <style>
    .cv-title {
        font-size: 2.1rem;
        font-weight: 700;
        margin-bottom: 0.1rem;
    }
    .cv-subtitle {
        color: #8a8a8a;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    .cv-card {
        background: #ffffff;
        border: 1px solid #f0dbe6;
        border-radius: 16px;
        padding: 1.2rem 1.4rem;
    }
    .cv-empty {
        background: %s;
        border: 2px dashed #f2b8d0;
        border-radius: 16px;
        padding: 2.5rem 1rem;
        text-align: center;
        color: #b56b8a;
    }
    .cv-label-row {
        margin-bottom: 0.65rem;
    }
    .cv-label-name {
        display: inline-block;
        background: %s;
        color: #ffffff;
        padding: 3px 12px;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .cv-score-track {
        background: #f4e3ec;
        border-radius: 999px;
        height: 6px;
        width: 100%%;
        overflow: hidden;
        margin-top: 3px;
    }
    .cv-score-fill {
        background: linear-gradient(90deg, #e5548f, #a05ee5);
        height: 100%%;
        border-radius: 999px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #e5548f, #a05ee5);
        color: white;
        border: none;
        border-radius: 999px;
        padding: 0.5rem 1.6rem;
        font-weight: 600;
    }
    .stButton>button:hover {
        opacity: 0.9;
        color: white;
    }
    </style>
    """
    % (BG_SOFT, ACCENT_COLOR),
    unsafe_allow_html=True,
)

st.markdown('<div class="cv-title">🖼️ 画像認識</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="cv-subtitle">画像をアップロードすると、写っているものを自動で解析します</div>',
    unsafe_allow_html=True,
)

# 画像ファイルのアップロード
file = st.file_uploader(
    "画像ファイルをアップロードしてください", type=["png", "jpg", "jpeg"]
)

content = file.getvalue() if file is not None else None

col_image, col_result = st.columns([1, 1], gap="large")

with col_image:
    if content is not None:
        st.image(content, use_container_width=True)
    else:
        st.markdown(
            """
            <div class="cv-empty">
                📤<br><br>
                ここに画像がまだありません<br>
                上のアップロード欄からファイルを選んでください
            </div>
            """,
            unsafe_allow_html=True,
        )

    analyze_clicked = st.button("✨ 解析をする", use_container_width=True)

with col_result:
    st.markdown("**解析結果**")

    if analyze_clicked and content is None:
        st.warning("先に画像をアップロードしてください。")

    elif analyze_clicked and content is not None:
        with st.spinner("画像を解析しています..."):
            response = get_response(content)

        if response.error.message:
            raise Exception(
                f"{response.error.message}\nFor more info on error messages, check: "
                "https://cloud.google.com/apis/design/errors"
            )

        labels = response.label_annotations

        if not labels:
            st.info("ラベルが検出されませんでした。")
        else:
            st.markdown('<div class="cv-card">', unsafe_allow_html=True)
            for label in labels:
                score_pct = round(label.score * 100)
                st.markdown(
                    f"""
                    <div class="cv-label-row">
                        <span class="cv-label-name">{label.description}</span>
                        <span style="float:right; color:#a05ee5; font-size:0.8rem; font-weight:600;">
                            {score_pct}%
                        </span>
                        <div class="cv-score-track">
                            <div class="cv-score-fill" style="width:{score_pct}%;"></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.caption("画像をアップロードして「解析をする」を押すと、ここに結果が表示されます。")

# import json
# import streamlit as st
# from google.cloud import vision


# # 定数の定義部分


# # Google APIキーの読み取り
# credentials_dict = json.loads(st.secrets["google_credentials"], strict=False)
# client = vision.ImageAnnotatorClient.from_service_account_info(info=credentials_dict)


# # 関数の定義部分


# # 画像処理 API とのやりとりとキャッシュ関数
# @st.cache_data
# def get_response(content):
#    image = vision.Image(content=content)
#    response = client.label_detection(image=image)


#    return response


# # 以下、表示部分
# st.markdown("# 画像認識")
# # 画像ファイルのアップロード
# file = st.file_uploader("画像ファイルをアップロードしてください")


# if file is not None:
#    # 画像の表示
#    content = file.getvalue()
#    st.image(content)
# # 画像解析
# if st.button("解析をする"):
#    response = get_response(content)
#    labels = response.label_annotations
#    st.write("Labels:")
#    if response.error.message:
#        raise Exception(
#            f"{response.error.message}\nFor more info on error messages, check: "
#            "https://cloud.google.com/apis/design/errors"
#        )
#    # 検出されたラベルを表示
#    for label in labels:
#        st.write(label.description)
