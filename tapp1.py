import streamlit as st
from google import genai
import time
import os

# 1. 앱 페이지 설정 (가장 먼저 실행)
st.set_page_config(
    page_title="대만 여행 꿀팁 🇹🇼",
    page_icon="✈️",
    layout="centered"
)

# --- [중요] API 키 안전하게 가져오기 ---
# 서버(Streamlit Cloud)의 'Secrets'에서 키를 가져옵니다.
# 코드를 깃허브에 올려도 키는 노출되지 않습니다.
try:
    if "GOOGLE_API_KEY" in st.secrets:
        GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    else:
        # 로컬에서 테스트할 때를 대비해 환경변수 등에서 찾거나 비워둡니다.
        # 주의: 여기에 직접 키를 적지 마세요!
        GOOGLE_API_KEY = None
except FileNotFoundError:
    GOOGLE_API_KEY = None

# 2. 제미나이 AI 연결 설정
client = None
if GOOGLE_API_KEY:
    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
    except Exception as e:
        st.error(f"연결 오류: {e}")
else:
    # 키가 없을 때 (아직 에러를 띄우지 않고 아래에서 안내 메시지 처리)
    pass

# 3. 타이틀
st.title("🇹🇼 AI 대만 여행 가이드")
st.caption("🚀 Powered by Gemini 2.5 Flash") 

st.markdown("""
반갑습니다! 
**"3박 4일 일정 짜줘"** 또는 **"지우펀 가는 버스 시간 알려줘"** 처럼 물어보세요.
""")

# 4. 메뉴 구성
tab1, tab2, tab3 = st.tabs(["🤖 AI 가이드", "📸 추천 명소", "🚇 교통 정보"])

# --- 탭 1: AI 가이드 ---
with tab1:
    st.header("무엇이든 물어보세요!")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("질문을 입력하세요..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            # 키가 설정되지 않았을 경우 사용자(개발자)에게 안내
            if client is None:
                st.error("⚠️ API 키가 설정되지 않았습니다.")
                st.info("Streamlit Cloud 배포 시 'Advanced Settings > Secrets'에 GOOGLE_API_KEY를 입력해야 합니다.")
            else:
                with st.spinner("최신 AI가 정보를 찾는 중입니다... 🇹🇼"):
                    try:
                        # Gemini 2.5 Flash 모델 사용
                        response = client.models.generate_content(
                            model="gemini-2.5-flash", 
                            contents=f"당신은 대만 여행 전문 가이드입니다. 한국어로 친절하게 답변해주세요. 질문: {prompt}"
                        )
                        
                        ai_response = response.text
                        st.markdown(ai_response)
                        st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    
                    except Exception as e:
                        if "404" in str(e):
                             st.error("모델 오류: gemini-2.5-flash를 찾을 수 없습니다. (gemini-1.5-flash로 변경해보세요)")
                        elif "429" in str(e):
                            st.error("사용량이 많아 잠시 제한되었습니다. 1분 뒤에 다시 시도해주세요.")
                        else:
                            st.error(f"오류가 발생했습니다: {e}")

# --- 탭 2: 추천 명소 ---
with tab2:
    st.subheader("대만 핫플레이스 Top 3")
    cols = st.columns(3)
    spots = [
        {"이름": "타이베이 101", "설명": "대만의 상징, 초고층 전망대"},
        {"이름": "지우펀", "설명": "홍등이 아름다운 골목길"},
        {"이름": "스린 야시장", "설명": "대만 최대의 미식 천국"},
    ]
    for i, spot in enumerate(spots):
        with cols[i]:
            st.info(f"**{spot['이름']}**")
            st.caption(spot['설명'])

# --- 탭 3: 교통 정보 ---
with tab3:
    st.header("교통 이용 꿀팁")
    st.success("💳 **이지카드(EasyCard)** 하나면 MRT, 버스, 편의점 해결!")
    st.warning("🚊 MRT(지하철) 내에서는 물 포함 음식물 섭취 금지 (벌금 부과)")