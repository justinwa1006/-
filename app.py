import streamlit as st
import urllib.parse
import requests
from bs4 import BeautifulSoup

# 1. 페이지 레이아웃 및 모바일 Viewport 설정
st.set_page_config(
    page_title="TRIP LOG · 스마트 여행 가이드",
    page_icon="✈️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. 고급 모바일 전용 CSS (토스/카카오 UI 스타일)
st.markdown("""
    <style>
    /* 전체 배경색 */
    .stApp {
        background-color: #F8F9FA;
        font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", sans-serif;
    }
    
    /* 상단 앱 배너 헤더 */
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

    /* 장소 추천 리스트 카드 UI */
    .card-container {
        background: #FFFFFF;
        padding: 16px;
        border-radius: 14px;
        margin-bottom: 12px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }
    .card-title {
        font-size: 17px;
        font-weight: 700;
        color: #111827;
    }
    .card-tag {
        background-color: #EFF6FF;
        color: #2563EB;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
    }
    .card-desc {
        font-size: 13px;
        color: #6B7280;
        margin-bottom: 12px;
    }

    /* 버튼 디테일 설정 */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        height: 40px !important;
        font-size: 13px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 앱 타이틀 헤더
st.markdown("""
    <div class="app-header">
        <div class="app-title">✈️ TRIP LOG</div>
        <div class="app-subtitle">한눈에 보는 지역별 명소 & 실시간 가이드</div>
    </div>
""", unsafe_allow_html=True)

# API 키 설정 사이드바
with st.sidebar:
    st.header("⚙️ 설정")
    gemini_api_key = st.text_input("Gemini API Key (선택)", type="password")

# 4. 도시 검색바
location = st.text_input("📍 어디로 떠나시나요?", placeholder="예: 강릉, 후쿠오카, 제주, 속초")

# 실시간 검색 연동 함수
def get_naver_search_results(query):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    encoded_query = urllib.parse.quote(query)
    url = f"https://search.naver.com/search.naver?where=nexearch&query={encoded_query}"
    
    try:
        res = requests.get(url, headers=headers, timeout=4)
        soup = BeautifulSoup(res.text, 'html.parser')
        places = []
        items = soup.select('.place_bluelink')
        for item in items[:4]:
            name = item.text.strip()
            if name and name not in [p['name'] for p in places]:
                places.append({'name': name})
        return places
    except Exception:
        return []

if location:
    loc_clean = location.strip()
    
    tab_recommend, tab_ai_planner = st.tabs(["✨ 명소 탐색", "🤖 AI 동선 플래너"])
    
    # ---------- 탭 1: 카테고리별 실시간 장소 카드 ----------
    with tab_recommend:
        st.write("")
        sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs(["🍽️ 맛집", "☕ 카페", "📸 관광지", "🌙 야경"])
        
        categories = [
            (sub_tab1, "맛집", "🍽️"),
            (sub_tab2, "카페", "☕"),
            (sub_tab3, "가볼만한곳", "📸"),
            (sub_tab4, "야경스팟", "🌙")
        ]
        
        for tab, cat_name, icon in categories:
            with tab:
                st.write("")
                search_term = f"{loc_clean} {cat_name}"
                places = get_naver_search_results(search_term)
                
                if places:
                    for p in places:
                        n_map = f"https://map.naver.com/v5/search/{urllib.parse.quote(loc_clean + ' ' + p['name'])}"
                        g_map = f"https://www.google.com/maps/search/{urllib.parse.quote(loc_clean + ' ' + p['name'])}"
                        
                        # 완성도 높은 모바일 카드 디자인
                        st.markdown(f"""
                            <div class="card-container">
                                <div class="card-header">
                                    <span class="card-title">{icon} {p['name']}</span>
                                    <span class="card-tag">실시간 인기</span>
                                </div>
                                <div class="card-desc">{loc_clean}의 인기 {cat_name} 명소입니다. 아래 버튼으로 지도와 상세 후기를 확인하세요.</div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.link_button("네이버 지도 보기", n_map, use_container_width=True)
                        with col2:
                            st.link_button("구글 지도 보기", g_map, use_container_width=True)
                        st.write("")
                else:
                    # 검색 결과가 부족할 경우의 기본 대응 카드
                    n_map = f"https://map.naver.com/v5/search/{urllib.parse.quote(search_term)}"
                    g_map = f"https://www.google.com/maps/search/{urllib.parse.quote(search_term)}"
                    
                    st.markdown(f"""
                        <div class="card-container">
                            <div class="card-header">
                                <span class="card-title">{icon} {loc_clean} {cat_name} 전체 검색</span>
                            </div>
                            <div class="card-desc">{loc_clean} 지역의 다양한 {cat_name} 정보를 지도 서비스에서 탐색합니다.</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.link_button(f"네이버에서 {cat_name} 보기", n_map, use_container_width=True)
                    with col2:
                        st.link_button(f"구글에서 {cat_name} 보기", g_map, use_container_width=True)

    # ---------- 탭 2: AI 일정 생성 ----------
    with tab_ai_planner:
        st.write("")
        st.subheader("🤖 AI 맞춤 동선 코스")
        
        duration = st.selectbox("여행 기간", ["당일치기", "1박 2일", "2박 3일", "3박 4일"])
        style = st.multiselect("선호 스타일", ["맛집 탐방", "감성 카페", "자연/힐링", "액티비티"], default=["맛집 탐방", "자연/힐링"])
        
        if st.button("✨ 맞춤 일정 생성하기", use_container_width=True):
            if not gemini_api_key:
                st.info("API Key가 지정되지 않아 기본 가이드 코스를 보여드립니다.")
                st.markdown(f"""
                ### 🗓️ {loc_clean} {duration} 추천 요약
                * **오전:** {loc_clean} 도착 후 대표 명소 방문
                * **점심:** 지역 향토 음식 맛집 식사
                * **오후:** 대표 감성 카페 및 주변 산책
                * **저녁:** 대표 야경 스팟 관람 후 일정 마무리
                """)
            else:
                try:
                    from google import genai
                    client = genai.Client(api_key=gemini_api_key)
                    
                    with st.spinner("AI가 동선을 계산 중입니다..."):
                        prompt = f"여행지: {loc_clean}, 기간: {duration}, 스타일: {', '.join(style)}. 이동 동선이 효율적인 여행 코스를 마크다운으로 작성해줘."
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt
                        )
                        st.markdown(response.text)
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")
