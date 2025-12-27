import streamlit as st
import requests
import re
import urllib.parse
from datetime import datetime, timedelta

# 1. 앱 페이지 설정 및 모바일 최적화 CSS 적용
st.set_page_config(
    page_title="대만 4박 5일 여행 가이드",
    page_icon="✈️",
    layout="centered"
)

# --- [UI/텍스트 가독성 강화를 위한 CSS] ---
st.markdown("""
    <style>
    /* 전체 배경색 및 기본 글자색 고정 (라이트모드 강제 효과) */
    .stApp { 
        background-color: #F8F9FA;
    }
    
    /* 모든 텍스트의 가시성 확보 */
    h1, h2, h3, p, span, li, label, div {
        color: #202124 !important; /* 어두운 회색으로 글자색 고정 */
    }

    /* 카드형 디자인 커스텀 */
    div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        background-color: white !important; 
        padding: 12px; 
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
        margin-bottom: 5px;
        border: 1px solid #EEEEEE;
    }

    /* 버튼 모바일 최적화 */
    .stButton > button {
        width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold;
        background-color: #4285F4 !important; 
        color: white !important; /* 버튼 글자는 흰색 유지 */
        border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* 버튼 내부 텍스트 색상 강제 (흰색) */
    .stButton > button p {
        color: white !important;
    }

    /* 탭 메뉴 가독성 강화 */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #E9ECEF !important; 
        border-radius: 10px 10px 0 0;
        padding: 10px 16px; 
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #4285F4 !important; 
    }
    .stTabs [aria-selected="true"] div {
        color: white !important; /* 선택된 탭 글자는 흰색 */
    }

    /* 정보 카드 내부 글자색 강조 */
    .info-card-text {
        color: #333333 !important;
        font-weight: 400;
    }
    
    /* 헤더 스타일링 */
    h1 { color: #1A73E8 !important; font-size: 1.8rem !important; text-align: center; font-weight: bold; }
    
    /* 성공/경고 메시지 내 글자색 */
    .stAlert p {
        color: #155724 !important; /* 성공 메시지는 어두운 초록 */
    }
    </style>
    """, unsafe_allow_html=True)

# --- [함수 설정] ---
def get_secret(key_name):
    return st.secrets.get(key_name, None)

NAVER_CLIENT_ID = get_secret("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = get_secret("NAVER_CLIENT_SECRET")
WEATHER_API_KEY = get_secret("OPENWEATHER_API_KEY")

def get_realtime_weather(city_name):
    if not WEATHER_API_KEY: return "☀️ 키 미등록"
    city_map = {"타이중": "Taichung", "타이베이": "Taipei"}
    city_en = city_map.get(city_name, "Taipei")
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_en}&appid={WEATHER_API_KEY}&units=metric&lang=kr"
    try:
        res = requests.get(url, timeout=5).json()
        return f"{res['main']['temp']}°C, {res['weather'][0]['description']}"
    except: return "⚠️ 정보 수신 불가"

def search_naver_blog(query, count=10):
    if not NAVER_CLIENT_ID: return [], "API 키 미등록"
    url = "https://openapi.naver.com/v1/search/blog.json"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    params = {"query": f"대만 {query}", "display": count, "sort": "date"}
    try:
        response = requests.get(url, headers=headers, params=params)
        return response.json().get('items', []), None
    except: return [], "연결 오류"

def clean_html(raw_html):
    return re.sub('<.*?>', '', raw_html)

def map_link_btn(place_name, btn_text=None):
    text = btn_text if btn_text else f"📍 {place_name} 지도보기"
    encoded_place = urllib.parse.quote(place_name)
    url = f"https://www.google.com/maps/search/{encoded_place}"
    st.markdown(f"""<a href="{url}" target="_blank" style="text-decoration: none;">
        <div style="display: block; background-color: #4285F4; color: white !important; padding: 12px; border-radius: 10px; font-size: 0.9em; font-weight: bold; margin-bottom: 10px; text-align: center;">{text}</div>
    </a>""", unsafe_allow_html=True)

def info_card(title, content, is_hotel=False):
    bg_color = "#f3e5f5" if is_hotel else "#e1f5fe"
    border_color = "#9c27b0" if is_hotel else "#0288d1"
    icon = "🏨" if is_hotel else "📌"
    st.markdown(f"""<div style="background-color: {bg_color}; padding: 15px; border-radius: 12px; border-left: 6px solid {border_color}; margin-bottom: 12px;">
        <b style="color: {border_color} !important; font-size: 1.1em;">{icon} {title}</b><br>
        <span style="font-size: 0.95em; color: #202124 !important; line-height: 1.6;">{content}</span>
    </div>""", unsafe_allow_html=True)

def display_blogs(query):
    st.markdown(f"<h4 style='color:#202124 !important;'>🔍 '{query}' 최신 정보 (블로그)</h4>", unsafe_allow_html=True)
    items, _ = search_naver_blog(query, count=10)
    if items:
        for item in items:
            st.markdown(f"- [{clean_html(item['title'])}]({item['link']})")
    else: st.write("관련 블로그 정보를 불러올 수 없습니다.")

# --- [메인 레이아웃] ---
st.title("대만 스마트 여행 가이드(by Changho)")
st.info("📅 12/31 ~ 1/4 부산 출발 (타이베이-타이중-타이베이)")

# --- [새로 추가된 우버 호출 섹션] ---
with st.container():
    st.subheader("🚖 우버(Uber) 호출")
    uber_dest = st.text_input("목적지 입력 (예: 린 호텔, 타이베이 101)", placeholder="목적지를 입력하세요", key="uber_input")
    if st.button("🚕 우버 앱 열기"):
        if uber_dest:
            encoded_dest = urllib.parse.quote(uber_dest)
            # Uber Deep Link: 목적지가 입력된 상태로 앱 실행
            uber_url = f"https://m.uber.com/ul/?action=setPickup&pickup=my_location&dropoff[nickname]={encoded_dest}"
            st.markdown(f'<p><a href="{uber_url}" target="_blank" style="text-decoration:none; color:white !important; background-color:#000000; padding:10px; border-radius:10px; display:block; text-align:center; font-weight:bold;">🚕 입력한 목적지로 우버 호출하기</a></p>', unsafe_allow_html=True)
        else:
            st.warning("목적지를 입력해주세요.")

st.divider()

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("실시간 날씨")
        target_city = st.selectbox("도시 선택", ["타이중", "타이베이","가오슝"])
        st.info(f"**{target_city} 현재:**\n{get_realtime_weather(target_city)}")
    with col2:
        st.subheader("🚀 지도 바로찾기")
        search_place = st.text_input("", placeholder="장소 입력 (예: 시먼딩 맛집)", key="map_input")
        if st.button("🔍 지도에서 찾기"):
            if search_place:
                encoded_search = urllib.parse.quote(search_place)
                map_url = f"https://www.google.com/maps/search/{encoded_search}"
                st.markdown(f'<p><a href="{map_url}" target="_blank" style="text-decoration:none; color:white !important; background-color:#1A73E8; padding:10px; border-radius:10px; display:block; text-align:center; font-weight:bold;">📍 클릭하여 지도 열기</a></p>', unsafe_allow_html=True)
            else:
                st.warning("장소 이름을 입력해주세요.")

st.divider()

tabs = st.tabs(["📅 나의 일정", "🔍 블로그 검색", "✅ 체크리스트"])

with tabs[0]:
    d_tabs = st.tabs(["1일", "2일", "3일", "4일", "5일"])
    
    with d_tabs[0]:
        st.subheader("1일차: 부산 출발 및 타이중 입성")
        st.success("🛫 **10:50** 김해 출발 → 🛬 **12:30** 타오위안 도착")
        info_card("이동: 타오위안 공항 → 타이중", "입국 심사 후 버스 터미널로 이동하여 '타이중(台中)'행 1623번(통합) 또는 1860번(국광) 버스 탑승 (약 2시간 소요)")
        info_card("체크인: 타이중 린 호텔 (The Lin)", "차오마(Chaoma) 터미널 하차 후 도보 5분 거리. 체크인 및 짐 풀기", is_hotel=True)
        map_link_btn("The Lin Hotel Taichung")
        
        info_card("타이중 국가 가극원", "독특한 곡선 구조의 건축물로 야경이 특히 아름답습니다.")
        map_link_btn("National Taichung Theater")
        info_card("숙박: 타이중 린 호텔 (The Lin)", "국가 가극원에서 택식로 5분", is_hotel=True)
        map_link_btn("The Lin Hotel Taichung")
        
        display_blogs("국가가극원 린호텔 타오위안공항 차오마터미널 ")

    with d_tabs[1]:
        st.subheader("2일차: 타이중 집중 관광")
        info_card("조식: 타이중 린 호텔 (The Lin)", "", is_hotel=True)
        
        info_card("동해대학교 루체예배당", "호텔 → 루체예배당 택시 20분")
        map_link_btn("Luce Memorial Chapel")
        info_card("춘수당 본점", "버블티가 처음 탄생한 곳, 동해대학교에서 택시로 20분")
        map_link_btn("Chun Shui Tang Siwei")
        info_card("심계신촌", "오래된 숙소를 개조해 만든 프리마켓, 춘수당에서 택시 15분")
        map_link_btn("Audit Village")
        info_card("궁원안과", "안과 개조한 디저트 카페. 심계신촌에서 택시 10분")
        map_link_btn("Miyahara")
        info_card("숙박: 타이중 린 호텔 (The Lin)", "궁원안과에서 택시 5분/도보가능", is_hotel=True)
        display_blogs("동해대학교 루체예배당 춘수당 심계신촌 궁원안과")

    with d_tabs[2]:
        st.subheader("3일차: 타이중 근교 투어")
        info_card("조식: 타이중 린 호텔 (The Lin)", "", is_hotel=True)
        info_card("일월담 (선문레이크)", "대만 최대의 호수입니다. 유람선 투어가 필수 코스입니다.")
        map_link_btn("Sun Moon Lake")
        info_card("고미습지", "환상적인 일몰을 볼 수 있는 습지입니다. 바람이 많이 불 수 있으니 주의하세요.")
        map_link_btn("Gaomei Wetlands")
        info_card("펑지아 야시장", "타이중 최대 야시장입니다. 먹거리가 가득합니다.")
        map_link_btn("Fengjia Night Market")
        info_card("숙박: 타이중 린 호텔 (The Lin)", "", is_hotel=True)
        display_blogs("일월담 고미습지 청지아 야시장 타이중일일투어")

    with d_tabs[3]:
        st.subheader("4일차: 타이중 → 타이베이 이동")
        info_card("이동: 타이중 호텔 → 타이베이 호텔", "린 호텔 체크아웃 후 고속철도(HSR) 타이중역으로 이동하여 타이베이역으로 1시간 10분 이동 ")
        info_card("체크인: 호텔 메트로폴리탄 프리미어 타이베이", "타이베이역 → 호텔까지 택시 15분", is_hotel=True)
        map_link_btn("Hotel Metropolitan Premier Taipei")
        info_card("국립고궁박물관", "호텔 → 국립고궁박물관까지 택시 20분")
        map_link_btn("National Palace Museum")
        info_card("랴오닝 야시장", "국립고궁박물관 → 랴오닝 야시장 택시 30분.")
        map_link_btn("Liaoning Night Market")
        display_blogs("타이베이고궁박물관 호텔메트로폴리탄프리미어타이베이")

    with d_tabs[4]:
        st.subheader("5일차: 귀국 준비 및 부산 도착")
        info_card("조식: 호텔 메트로폴리탄 프리미어 타이베이", "마지막 조식 후 체크아웃 준비", is_hotel=True)
        info_card("이동: 호텔 → 타오위안 공항", "호텔 앞에서 공항 버스(1960번 등) 탑승 60분")
        info_card("타오위안 국제공항", "출발 3시간 전 도착 권장. 면세점 쇼핑 및 식사")
        st.success("🛫 **13:25** 타오위안 국제공항 출발 → **김해행**")
        map_link_btn("Taoyuan Airport Terminal 1")
        display_blogs("타오위안 공항 면세점")

with tabs[1]:
    st.header("🔍 실시간 장소 정보 검색")
    user_q = st.text_input("장소 이름 입력", placeholder="예: 타이중 우육면, 타이베이 딤섬", key="search_tab_input")
    if st.button("최신 블로그 10개 찾기", type="primary"):
        if user_q:
            with st.spinner(f"'{user_q}' 검색 중..."):
                items, err = search_naver_blog(user_q, count=10)
                if items:
                    for i, item in enumerate(items, 1):
                        st.markdown(f"**{i}. [{clean_html(item['title'])}]({item['link']})**")
                        st.caption(f"📅 {item['postdate']}")
                        st.divider()
                else: st.warning("결과가 없습니다.")
        else: st.error("검색어를 입력해 주세요.")

with tabs[2]:
    st.header("✅ 필수 체크리스트")
    st.checkbox("이지카드 충전 및 데이터(eSIM/유심) 확인")
    st.checkbox("110V를 사용 '돼지코' 어댑터")
    st.info("연말연시 대만은 한국보다 따뜻하지만 일교차가 큽니다.")
    st.info("가벼운 외투, 우산/우비 필수, 레이어드 복장를 챙기세요!")   
    st.info("입국 시 디지털 입국신고서 작성, 육가공품 반입 금지, 전자담배 금지")

