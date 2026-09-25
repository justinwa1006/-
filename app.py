import streamlit as st
import urllib.parse
import requests
from bs4 import BeautifulSoup

# 1. 페이지 및 모바일 레이아웃 설정
st.set_page_config(
    page_title="TRIP LOG · 여행 플래너",
    page_icon="✈️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. 고급 모바일 앱 UI (Toss 스타일 CSS 적용)
st.markdown("""
    <style>
    /* 기본 배경 및 글꼴 */
    .stApp {
        background-color: #F2F4F6;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* 상단 앱 타이틀 헤더 */
    .app-header {
        background: linear-gradient(135deg, #3182F6 0%, #1B64DA 100%);
        padding: 24px 20px;
        border-radius: 20px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 8px 16px rgba(49, 130, 246, 0.25);
    }
    .app-title { font-size: 24px; font-weight: 800; margin: 0; }
    .app-subtitle { font-size: 14px; opacity: 0.9; margin-top: 6px; }

    /* 장소 추천 카드 디자인 */
    .place-card {
        background: #FFFFFF;
        padding: 18px;
        border-radius: 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid #E5E8EB;
    }
    .place-title {
        font-size: 17px;
        font-weight: 700;
        color: #191F28;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .place-desc {
        font-size: 13px;
        color: #8B95A1;
        margin-top: 6px;
        line-height: 1.4;
    }
    
    /* 태그 스타일 */
    .badge-live {
        background-color: #E8F3FF;
        color: #3182F6;
        padding: 4px 8px;
        border-radius: 8px;
        font-size: 11px;
        font-weight: 700;
    }

    /* 지도 버튼 스타일 커스텀 */
    div[data-testid="stHorizontalBlock"] {
        gap: 8px;
    }
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        border: none !important;
        height: 42px !important;
        transition: all 0.2s ease;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 앱 헤더 영역
st.markdown("""
    <div class="app-header">
        <div class="app-title">✈️ TRIP LOG</div>
        <div class="app-subtitle">스마트한 여행 명소 검색 & AI 동선 추천</div>
    </div>
""", unsafe_allow_html=True)

# 사이드바 설정 (API 키)
with st.sidebar:
    st.header("⚙️ 앱 설정")
    gemini_api_key = st.text_input("Gemini API Key (선택)", type="password", help="AI 맞춤 코스 생성을 원하시면 입력해주세요.")

# 4. 메인 입력 창 (검색바)
location = st.text_input("📍 어디로 떠나시나요?", placeholder="예: 강릉, 후쿠오카, 제주, 속초")

# 실시간 검색 함수
def get_naver_search_results(query):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    encoded_query = urllib.parse.quote(query)
    url = f"https://search.naver.com/search.naver?where=nexearch&query={encoded_query}"
    
    try:
        res = requests.get(url, headers=headers, timeout=4)
        soup = BeautifulSoup(res.text, 'html.parser')
        places = []
        items = soup.select('.place_bluelink')
        for item in items[:5]:
            name = item.text.strip()
            if name and name not in [p['name'] for p in places]:
                places.append({'name': name, 'desc': '실시간 인기 추천 장소'})
        return places
    except Exception:
        return []

if location:
    loc_clean = location.strip()
    
    # 메인 탭 구성
    tab_recommend, tab_ai_planner = st.tabs(["✨ 명소·맛집 탐색", "🤖 AI 동선 플래너"])
    
    # ---------- 탭 1: 명소 탐색 ----------
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
                        
                        st.markdown(f"""
                            <div class="place-card">
                                <div class="place-title">
                                    <span>{icon} {p['name']}</span>
                                    <span class="badge-live">인기</span>
                                </div>
                                <div class="place-desc">{loc_clean} 인근 인기 {cat_name}입니다.</div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            st.link_button("네이버 지도", n_map, use_container_width=True)
                        with c2:
                            st.link_button("구글 지도", g_map, use_container_width=True)
                        st.write("")
                else:
                    st.info(f"'{loc_clean} {cat_name}' 바로 검색하기")
                    n_map = f"https://map.naver.com/v5/search/{urllib.parse.quote(search_term)}"
                    g_map = f"https://www.google.com/maps/search/{urllib.parse.quote(search_term)}"
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.link_button(f"네이버에서 {cat_name} 보기", n_map, use_container_width=True)
                    with c2:
                        st.link_button(f"구글에서 {cat_name} 보기", g_map, use_container_width=True)

    # ---------- 탭 2: AI 플래너 ----------
    with tab_ai_planner:
        st.write("")
        st.markdown("""
            <div style="background: white; padding: 20px; border-radius: 16px; border: 1px solid #E5E8EB;">
                <h4 style="margin: 0 0 10px 0; color: #191F28;">🤖 AI 맞춤 일정 설계</h4>
                <p style="margin: 0; color: #8B95A1; font-size: 13px;">동선을 고려한 최고의 여행 일정을 생성합니다.</p>
            </div>
        """, unsafe_allow_html=True)
        st.write("")
        
        duration = st.selectbox("여행 기간", ["당일치기", "1박 2일", "2박 3일", "3박 4일"])
        style = st.multiselect("여행 스타일", ["맛집 탐방", "감성 카페", "자연/힐링", "액티비티", "문화/전시", "쇼핑"], default=["맛집 탐방", "자연/힐링"])
        
        if st.button("✨ 맞춤 일정 생성하기", use_container_width=True):
            if not gemini_api_key:
                st.info("API Key가 지정되지 않아 기본 가이드 코스를 보여드립니다.")
                st.markdown(f"""
                ### 🗓️ {loc_clean} {duration} 추천 일정
                * **오전:** {loc_clean} 중심 명소 탐방
                * **점심:** 대표 향토 맛집 식사
                * **오후:** 시그니처 감성 카페 및 주변 산책
                * **저녁:** 야시장 또는 야경 스팟 방문
                """)
            else:
                try:
                    from google import genai
                    client = genai.Client(api_key=gemini_api_key)
                    
                    with st.spinner("AI가 최적의 동선을 계산하는 중입니다..."):
                        prompt = f"여행지: {loc_clean}, 기간: {duration}, 스타일: {', '.join(style)}. 이동 동선이 효율적인 여행 코스를 마크다운으로 작성해줘."
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt
                        )
                        st.markdown(response.text)
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")
