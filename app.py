import streamlit as st
import urllib.parse
import requests
from bs4 import BeautifulSoup
import os

# 1. 페이지 및 모바일 전용 Layout 설정
st.set_page_config(
    page_title="스마트 AI 여행 플래너",
    page_icon="✈️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 모바일 UI 스타일링
st.markdown("""
    <style>
    .main { padding: 0.5rem; }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 2.8rem;
        background-color: #3182F6;
        color: white;
        font-weight: bold;
        border: none;
    }
    .place-card {
        padding: 16px;
        border-radius: 12px;
        background-color: #F8F9FA;
        margin-bottom: 12px;
        border: 1px solid #E5E8EB;
    }
    .tag {
        display: inline-block;
        background-color: #E8F3FF;
        color: #1B64DA;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: bold;
        margin-left: 6px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("✈️ 스마트 AI 여행 플래너")
st.caption("실시간 명소 검색과 AI 맞춤 일정 생성을 한 번에 해결하세요.")

# 사이드바: API 키 설정
with st.sidebar:
    st.header("⚙️ 설정")
    gemini_api_key = st.text_input("Gemini API Key (선택)", type="password", help="AI 코스 생성을 이용하려면 Google AI Studio에서 발급받은 키를 입력하세요.")

# 2. 메인 입력폼
location = st.text_input("📍 어디로 떠나시나요?", placeholder="예: 강릉, 후쿠오카, 제주, 속초")

# 네이버 실시간 장소 검색 연동 함수
def get_naver_search_results(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    encoded_query = urllib.parse.quote(query)
    url = f"https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query={encoded_query}"
    
    try:
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 네이버 플레이스 장소 추출 시도
        places = []
        items = soup.select('.place_bluelink')
        for item in items[:5]:
            name = item.text.strip()
            if name and name not in [p['name'] for p in places]:
                places.append({'name': name, 'desc': '실시간 인기 장소'})
        return places
    except Exception:
        return []

if location:
    loc_clean = location.strip()
    
    st.divider()
    
    # 3. 메인 탭 구성
    tab_recommend, tab_ai_planner = st.tabs(["🔍 명소·맛집 탐색", "🤖 AI 코스 추천"])
    
    # ------------------ 탭 1: 카테고리별 추천 ------------------
    with tab_recommend:
        st.subheader(f"📍 '{loc_clean}' 추천 스팟")
        
        sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs(["🍽️ 맛집", "☕ 카페", "📸 관광지", "🌙 야경"])
        
        categories = [
            (sub_tab1, "맛집", "🍽️"),
            (sub_tab2, "카페", "☕"),
            (sub_tab3, "가볼만한곳", "📸"),
            (sub_tab4, "야경스팟", "🌙")
        ]
        
        for tab, cat_name, icon in categories:
            with tab:
                search_term = f"{loc_clean} {cat_name}"
                places = get_naver_search_results(search_term)
                
                if places:
                    for p in places:
                        n_map = f"https://map.naver.com/v5/search/{urllib.parse.quote(loc_clean + ' ' + p['name'])}"
                        g_map = f"https://www.google.com/maps/search/{urllib.parse.quote(loc_clean + ' ' + p['name'])}"
                        
                        st.markdown(f"""
                            <div class="place-card">
                                <h4 style="margin:0 0 6px 0; color:#191F28;">{icon} {p['name']} <span class="tag">실시간</span></h4>
                                <p style="margin:0; color:#4E5968; font-size:14px;">{loc_clean} 인근 인기 {cat_name}입니다.</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            st.link_button("네이버 지도", n_map)
                        with c2:
                            st.link_button("구글 지도", g_map)
                        st.write("")
                else:
                    st.info(f"'{loc_clean} {cat_name}' 바로 검색하기")
                    n_map = f"https://map.naver.com/v5/search/{urllib.parse.quote(search_term)}"
                    g_map = f"https://www.google.com/maps/search/{urllib.parse.quote(search_term)}"
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.link_button(f"네이버에서 {cat_name} 보기", n_map)
                    with col2:
                        st.link_button(f"구글에서 {cat_name} 보기", g_map)

    # ------------------ 탭 2: AI 동선/일정 짜기 ------------------
    with tab_ai_planner:
        st.subheader("🤖 AI 여행 일정 생성기")
        st.write("여행 스타일과 기간을 정해주시면 최적의 동선을 만들어 드립니다.")
        
        duration = st.selectbox("여행 기간", ["당일치기", "1박 2일", "2박 3일", "3박 4일"])
        style = st.multiselect("여행 스타일", ["맛집 탐방", "감성 카페", "자연/힐링", "액티비티", "문화/전시", "쇼핑"], default=["맛집 탐방", "자연/힐링"])
        
        if st.button("✨ 맞춤 일정 생성하기"):
            if not gemini_api_key:
                # API 키가 없을 때 기본 템플릿 제공
                st.warning("사이드바에 Gemini API Key를 입력하시면 더 정교한 AI 일정을 생성할 수 있습니다. (기본 샘플 출력을 진행합니다.)")
                st.markdown(f"""
                ### 🗓️ {loc_clean} {duration} 추천 일정 (기본)
                
                **[1일차: 핵심 관광 및 대표 맛집]**
                * **오전:** {loc_clean} 대표 명소 산책 및 사진 촬영
                * **점심:** {loc_clean} 지역 향토 음식 맛집 방문
                * **오후:** 뷰가 좋은 시그니처 카페에서 휴식
                * **저녁:** 로컬 야시장 또는 유명 식당 이용
                * **야간:** 대표 야경 스팟 방문 후 일정 마무리
                """)
            else:
                try:
                    from google import genai
                    client = genai.Client(api_key=gemini_api_key)
                    
                    with st.spinner("AI가 동선을 계산하여 최적의 코스를 만드는 중입니다..."):
                        prompt = f"""
                        여행지: {loc_clean}
                        기간: {duration}
                        선호 스타일: {', '.join(style)}
                        
                        위 조건에 맞춰 이동 동선이 효율적인 여행 일정을 상세히 짜주세요.
                        각 코스마다 이동에 도움이 되는 팁과 추천 음식/활동을 포함해 깔끔한 마크다운 형식으로 작성해주세요.
                        """
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt
                        )
                        st.markdown(response.text)
                except Exception as e:
                    st.error(f"AI 일정 생성 중 오류가 발생했습니다: {e}")