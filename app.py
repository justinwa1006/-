import streamlit as st
import requests
import urllib.parse

# 1. 페이지 및 모바일 Viewport 설정
st.set_page_config(
    page_title="TRIP LOG · TOP 10 가이드",
    page_icon="✈️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 2. 고급 모바일 앱 스타일링
st.markdown("""
    <style>
    .stApp {
        background-color: #F8F9FA;
        font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", sans-serif;
    }
    .app-header {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        padding: 22px 18px;
        border-radius: 18px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.2);
    }
    .app-title { font-size: 22px; font-weight: 800; letter-spacing: -0.5px; }
    .app-subtitle { font-size: 13px; opacity: 0.9; margin-top: 4px; }
    .place-card {
        background-color: white;
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 12px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .place-title { font-size: 16px; font-weight: 700; color: #1F2937; }
    .place-category { font-size: 12px; color: #6B7280; margin-bottom: 6px; }
    .place-address { font-size: 13px; color: #4B5563; }
    </style>
""", unsafe_allow_html=True)

# 3. 앱 타이틀 헤더
st.markdown("""
    <div class="app-header">
        <div class="app-title">✈️ TRIP LOG</div>
        <div class="app-subtitle">네이버 실시간 검색 기반 TOP 10 가이드</div>
    </div>
""", unsafe_allow_html=True)

# 사이드바 설정 (네이버 API Key 입력)
with st.sidebar:
    st.header("⚙️ 설정")
    naver_client_id = st.text_input("Naver Client ID", type="password", help="네이버 개발자 센터에서 발급받은 Client ID")
    naver_client_secret = st.text_input("Naver Client Secret", type="password", help="네이버 개발자 센터에서 발급받은 Client Secret")

# 네이버 지역 검색 API 함수
@st.cache_data(show_spinner=False)
def fetch_naver_places(client_id, client_secret, loc, cat):
    query = f"{loc} {cat}"
    url = f"https://openapi.naver.com/v1/search/local.json?query={urllib.parse.quote(query)}&display=10&sort=comment"
    
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('items', [])
    else:
        return None

# 장소 리스트 출력 함수
def render_places(client_id, client_secret, loc, cat):
    places = fetch_naver_places(client_id, client_secret, loc, cat)
    
    if places is None:
        st.error("API 요청에 실패했습니다. Client ID와 Secret을 확인해 주세요.")
        return
    
    if not places:
        st.info("검색 결과가 없습니다.")
        return

    for idx, item in enumerate(places, 1):
        # HTML 태그 제거
        title = item['title'].replace('<b>', '').replace('</b>', '')
        category = item['category']
        address = item['address'] if item['address'] else item['roadAddress']
        map_url = f"https://map.naver.com/v5/search/{urllib.parse.quote(f'{loc} {title}')}"
        
        st.markdown(f"""
            <div class="place-card">
                <div class="place-title">TOP {idx}. {title}</div>
                <div class="place-category">🏷️ {category}</div>
                <div class="place-address">📍 {address}</div>
                <div style="margin-top: 8px;">
                    <a href="{map_url}" target="_blank" style="color: #2563EB; font-size: 13px; text-decoration: none; font-weight: 600;">
                        👉 네이버 지도로 확인하기
                    </a>
                </div>
            </div>
        """, unsafe_allow_html=True)

# 4. 메인 화면
location = st.text_input("📍 어디로 떠나시나요?", value="제주도", placeholder="예: 제주도, 강릉, 속초")

if location:
    loc_clean = location.strip()
    
    sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs(["🍽️ 맛집", "☕ 카페", "📸 관광지", "🌙 야경"])
    
    if not naver_client_id or not naver_client_secret:
        st.warning("⚠️ 왼쪽 사이드바에 네이버 API Key (Client ID & Secret)를 입력해주세요.")
    else:
        with sub_tab1:
            st.write("")
            render_places(naver_client_id, naver_client_secret, loc_clean, "맛집")
            
        with sub_tab2:
            st.write("")
            render_places(naver_client_id, naver_client_secret, loc_clean, "카페")
            
        with sub_tab3:
            st.write("")
            render_places(naver_client_id, naver_client_secret, loc_clean, "가볼만한곳")
            
        with sub_tab4:
            st.write("")
            render_places(naver_client_id, naver_client_secret, loc_clean, "야경")
