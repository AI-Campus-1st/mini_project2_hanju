import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt

st.title('자전거 대여소 개선방안')

load_dotenv('11.env')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME')

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

accident_df = pd.read_sql("SELECT * FROM accident_rank", con=engine)
rental_df = pd.read_csv('TB_PTP_SHBK_RNTL_SPOT_INFO.csv', encoding='utf-8-sig')
danger_df = pd.read_sql("SELECT * FROM danger_rank", con=engine)

LAT_DIFF = 0.009
LON_DIFF = 0.011

st.markdown(
    "<h3 style='color: #FF5733;'>자전거 사고중 대부분은 대여소 인근에서 발생한다.</h3>",
    unsafe_allow_html=True
)

# 사고많은 지점

accident_존재여부 = []
accident_대여소명 = []

for i in range(len(accident_df)):
    사고_위도 = accident_df.loc[i, '위도']
    사고_경도 = accident_df.loc[i, '경도']
    찾은_대여소 = None

    for j in range(len(rental_df)):
        대여소_위도 = rental_df.loc[j, 'CMWNR_BIKE_RNTL_SMALL_LTTD']
        대여소_경도 = rental_df.loc[j, 'CMWNR_BIKE_RNTL_SMALL_LNGTD']
        대여소_이름 = rental_df.loc[j, 'CMWNR_BIKE_RNTL_SMALL_NM']

        위도차이 = abs(사고_위도 - 대여소_위도)
        경도차이 = abs(사고_경도 - 대여소_경도)

        if 위도차이 <= LAT_DIFF and 경도차이 <= LON_DIFF:
            찾은_대여소 = 대여소_이름
            break

    if 찾은_대여소 is not None:
        accident_존재여부.append('있음')
        accident_대여소명.append(찾은_대여소)
    else:
        accident_존재여부.append('없음')
        accident_대여소명.append('-')

accident_df['대여소_존재여부'] = accident_존재여부
accident_df['가까운_대여소명'] = accident_대여소명


# 부상위험 높은 지점

danger_존재여부 = []
danger_대여소명 = []

for i in range(len(danger_df)):
    사고_위도 = danger_df.loc[i, '위도']
    사고_경도 = danger_df.loc[i, '경도']
    찾은_대여소 = None

    for j in range(len(rental_df)):
        대여소_위도 = rental_df.loc[j, 'CMWNR_BIKE_RNTL_SMALL_LTTD']
        대여소_경도 = rental_df.loc[j, 'CMWNR_BIKE_RNTL_SMALL_LNGTD']
        대여소_이름 = rental_df.loc[j, 'CMWNR_BIKE_RNTL_SMALL_NM']

        위도차이 = abs(사고_위도 - 대여소_위도)
        경도차이 = abs(사고_경도 - 대여소_경도)

        if 위도차이 <= LAT_DIFF and 경도차이 <= LON_DIFF:
            찾은_대여소 = 대여소_이름
            break

    if 찾은_대여소 is not None:
        danger_존재여부.append('있음')
        danger_대여소명.append(찾은_대여소)
    else:
        danger_존재여부.append('없음')
        danger_대여소명.append('-')

danger_df['대여소_존재여부'] = danger_존재여부
danger_df['가까운_대여소명'] = danger_대여소명


# ===== 6. 화면에 지도로 보여주기 =====
st.write("사고 다발생지점 상위 10지점 위치")
map_df = accident_df[['위도', '경도']].rename(columns={'위도': 'lat', '경도': 'lon'})
st.map(map_df) 

st.write("고위험지점 상위 10지점 위치")
map_df = danger_df[['위도', '경도']].rename(columns={'위도': 'lat', '경도': 'lon'})
st.map(map_df) 

# ===== 5. 화면에 표로 보여주기 =====
st.subheader("사고 다발생지점 대여소 매칭 결과")
st.dataframe(accident_df, width='stretch')

st.subheader("고위험지점 대여소 매칭 결과")
st.dataframe(danger_df, width='stretch')

st.markdown(
    "<h3 style='color: #FF5733;'>사고 다발생지점 상위 10곳 중 6곳 <br> 고위험지점 상위 10곳 중 5곳이 <br> 근방 1km에 자전거 대여소가 위치한다. </h3>",
    unsafe_allow_html=True
)




helmet_df = pd.read_sql("SELECT * FROM helmet_rate", con=engine)

전국_df = helmet_df[
    (helmet_df['시도'] == '전국') &
    (helmet_df['구분1'] == '전체') &
    (helmet_df['구분2'] == '소계')
]


st.subheader('중증외상 환자 중 자전거 헬멧 착용률')

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def 파이차트_그리기(df, 제목):
    라벨 = ['착용', '미착용', '미상']
    값 = [
        df['착용_분율'].values[0],
        df['미착용_분율'].values[0],
        df['미상_분율'].values[0]
    ]

    fig, ax = plt.subplots()
    ax.pie(값, labels=라벨, autopct='%.1f%%', startangle=90)
    ax.set_title(제목)
    ax.axis('equal')  # 원형 유지
    return fig

# ===== 5. 화면에 나란히 표시 =====

남자_df = helmet_df[
    (helmet_df['시도'] == '전국') &
    (helmet_df['구분1'] == '성별') &
    (helmet_df['구분2'] == '남자')
]

여자_df = helmet_df[
    (helmet_df['시도'] == '전국') &
    (helmet_df['구분1'] == '성별') &
    (helmet_df['구분2'] == '여자')
]
col1, col2 = st.columns(2)

with col1:
    st.write("남자")
    fig_남자 = 파이차트_그리기(남자_df, "남자 헬멧 착용률")
    st.pyplot(fig_남자)

with col2:
    st.write("여자")
    fig_여자 = 파이차트_그리기(여자_df, "여자 헬멧 착용률")
    st.pyplot(fig_여자)


st.markdown(
    "<h2 style='color: #336633;'> 이제는 자전거만 대여하는 것이 아니라 헬멧또한 대여 및 의무 착용을 통해 치명상을 줄여야한다.</h2>",
    unsafe_allow_html=True
)
