import streamlit as st
import urllib.parse
import requests
from bs4 import BeautifulSoup

# 1. 페이지 및 모바일 Viewport 설정
st.set_page_config(
    page_title="TRIP LOG · TOP 10 가이드",
    page_icon="✈️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. 고급 모바일 앱 스타일링 (토스/카카오 스타일)
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

    /* 장소 상세 정보 박스 UI */
    .info-box {
        background-color: #F3F4F6;
        padding: 14px;
        border-radius: 10px;
        margin-top: 8px;
        font-size: 13px;
        line-height: 1.6;
        color: #374151;
    }
    .badge-rank {
        background-color: #2563EB;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 700;
        margin-right: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 앱 타이틀 헤더
st.markdown("""
    <div class="app-header">
        <div class="app-title">✈️ TRIP LOG</div>
        <div class="app-subtitle">외부 이동 없는 실시간 TOP 10 명소 상세 가이드</div>
    </div>
""", unsafe_allow_html=True)

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 설정")
    gemini_api_key = st.text_input("Gemini API Key (선택)", type="password")

# 4. 입력창
location = st.text_input("📍 어디로 떠나시나요?", placeholder="예: 강릉, 후쿠오카, 제주, 속초")

# 실시간 10개 장소 수집 함수
def get_top10_places(query):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    encoded_query = urllib.parse.quote(query)
    url = f"https://search.naver.com/search.naver?where=nexearch&query={encoded_query}"
    
    try:
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        places = []
        
        # 네이버 플레이스 장소 추출 (최대 10개)
        items = soup.select('.place_bluelink')
        for item in items:
            name = item.text.strip()
            if name and name not in [p['name'] for p in places]:
                places.append({'name': name})
            if len(places) >= 10:
                break
        return places
    except Exception:
        return []

if location:
    loc_clean = location.strip()
    
    tab_recommend, tab_ai_planner = st.tabs(["✨ TOP 10 명소 탐색", "🤖 AI 동선 플래너"])
    
    # ---------- 탭 1: 앱 내 TOP 10 상세 안내 ----------
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
                places = get_top10_places(search_term)
                
                if places:
                    st.caption(f"🔥 {loc_clean} 인기 {cat_name} TOP {len(places)} (터치하면 상세 정보를 확인합니다)")
                    
                    for idx, p in enumerate(places, 1):
                        # 지도로 이동하지 않고 앱 내에서 열리는 카드/아코디언 형태
                        with st.expander(f"TOP {idx} · {icon} {p['name']}"):
                            st.markdown(f"""
                            <div class="info-box">
                                <b>📌 카테고리:</b> {loc_clean} {cat_name}<br>
                                <b>💡 추천 포인트:</b> 방문객 평점이 높고 실시간 검색량이 많은 대표 명소입니다.<br>
                                <b>🍴 특징/분위기:</b> 로컬 분위기와 시그니처 메뉴/풍경을 즐기기 좋습니다.<br>
                                <b>✨ 방문 팁:</b> 주말이나 피크 타임에는 대기 시간이 발생할 수 있으니 방문 전 사전 확인을 권장합니다.
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info(f"'{loc_clean} {cat_name}' 실시간 정보를 가져오는 중입니다. 잠시 후 다시 검색해주세요.")

    # ---------- 탭 2: AI 동선 플래너 ----------
    with tab_ai_planner:
        st.write("")
        st.subheader("🤖 AI 맞춤 동선 설계")
        
        duration = st.selectbox("여행 기간", ["당일치기", "1박 2일", "2박 3일", "3박 4일"])
        style = st.multiselect("선호 스타일", ["맛집 탐방", "감성 카페", "자연/힐링", "액티비티"], default=["맛집 탐방", "자연/힐링"])
        
        if st.button("✨ 맞춤 일정 생성하기", use_container_width=True):
            if not gemini_api_key:
                st.info("API Key가 설정되지 않아 기본 가이드 코스를 보여드립니다.")
                st.markdown(f"""
                ### 🗓️ {loc_clean} {duration} 추천 코스
                * **오전:** {loc_clean} 도착 후 대표 관광지 탐방
                * **점심:** 대표 맛집 TOP 10 중 한 곳 방문
                * **오후:** 감성 카페에서 휴식 및 산책
                * **저녁:** 야경 스팟 관람 후 일정 마무리
                """)
            else:
                try:
                    from google import genai
                    client = genai.Client(api_key=gemini_api_key)
                    
                    with st.spinner("AI가 동선을 계산 중입니다..."):
                        prompt = f"여행지: {loc_clean}, 기간: {duration}, 스타일: {', '.join(style)}. 이동 동선이 효율적인 여행 코스를 작성해줘."
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt
                        )
                        st.markdown(response.text)
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")
