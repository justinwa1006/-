import streamlit as st
import google.generativeai as genai
import urllib.parse
import re

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
    </style>
""", unsafe_allow_html=True)

# 3. 앱 타이틀 헤더
st.markdown("""
    <div class="app-header">
        <div class="app-title">✈️ TRIP LOG</div>
        <div class="app-subtitle">AI 기반 실시간 TOP 10 명소 가이드</div>
    </div>
""", unsafe_allow_html=True)

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 설정")
    gemini_api_key = st.text_input("Gemini API Key", type="password", help="Google AI Studio에서 발급받은 API Key를 입력하세요.")

# 국내/해외 구분 함수 (한글 키워드 기반 판단)
def is_korean_location(loc_name):
    # 주요 해외 도시 키워드 체크
    foreign_keywords = ['후쿠오카', '도쿄', '오사카', '교토', '삿포로', '오키나와', '방콕', '다낭', '나트랑', '발리', '파리', '런던', '뉴욕', '하와이', '괌', '사이판', '싱가포르', '홍콩', '타이베이', '대만']
    for fk in foreign_keywords:
        if fk in loc_name:
            return False
    return True

# 4. 입력창
location = st.text_input("📍 어디로 떠나시나요?", value="제주도", placeholder="예: 제주도, 강릉, 후쿠오카, 속초")

if location:
    loc_clean = location.strip()
    is_korea = is_korean_location(loc_clean)
    
    tab_recommend, tab_ai_planner = st.tabs(["✨ TOP 10 명소 탐색", "🤖 AI 동선 플래너"])
    
    # ---------- 탭 1: AI 기반 TOP 10 상세 안내 ----------
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
                if not gemini_api_key:
                    st.warning("⚠️ 왼쪽 사이드바에 Gemini API Key를 입력해주세요.")
                else:
                    try:
                        genai.configure(api_key=gemini_api_key)
                        model = genai.GenerativeModel('gemini-3.6-flash')
                        
                        map_type_str = "네이버 지도" if is_korea else "구글 지도"
                        
                        with st.spinner(f"AI가 {loc_clean} {cat_name} TOP 10을 불러오는 중입니다..."):
                            prompt = f"""
                            여행지 '{loc_clean}'의 대표 {cat_name} TOP 10 장소를 추천해줘.
                            각 장소마다 아래 서식을 **반드시 동일하게 준수**해서 작성해줘:

                            ### TOP [번호]. {icon} [장소 이름]
                            * **특징/분위기:** [내용]
                            * **대표 메뉴/볼거리:** [내용]
                            * **방문 팁:** [내용]
                            ---
                            """
                            response = model.generate_content(prompt)
                            raw_text = response.text
                            
                            # 지도 링크 자동 삽입 처리
                            lines = raw_text.split('\n')
                            formatted_lines = []
                            current_place = ""
                            
                            for line in lines:
                                formatted_lines.append(line)
                                if line.startswith("### TOP"):
                                    # 장소 이름 추출
                                    place_match = re.search(r'### TOP \d+\.\s*(?:[^\s]+\s+)?(.+)', line)
                                    if place_match:
                                        place_name = place_match.group(1).strip()
                                        query_str = urllib.parse.quote(f"{loc_clean} {place_name}")
                                        
                                        if is_korea:
                                            map_url = f"https://map.naver.com/v5/search/{query_str}"
                                            link_md = f"* 📍 **위치 보기:** [네이버 지도로 확인하기]({map_url})"
                                        else:
                                            map_url = f"https://www.google.com/maps/search/?api=1&query={query_str}"
                                            link_md = f"* 📍 **위치 보기:** [구글 지도로 확인하기]({map_url})"
                                        
                                        formatted_lines.append(link_md)
                            
                            st.markdown('\n'.join(formatted_lines))
                    except Exception as e:
                        st.error(f"오류가 발생했습니다: {e}")

    # ---------- 탭 2: AI 동선 플래너 ----------
    with tab_ai_planner:
        st.write("")
        st.subheader("🤖 AI 맞춤 동선 설계")
        
        duration = st.selectbox("여행 기간", ["당일치기", "1박 2일", "2박 3일", "3박 4일"])
        style = st.multiselect("선호 스타일", ["맛집 탐방", "감성 카페", "자연/힐링", "액티비티"], default=["맛집 탐방", "자연/힐링"])
        
        if st.button("✨ 맞춤 일정 생성하기", use_container_width=True):
            if not gemini_api_key:
                st.warning("⚠️ 사이드바에 Gemini API Key를 입력해주세요.")
            else:
                try:
                    genai.configure(api_key=gemini_api_key)
                    model = genai.GenerativeModel('gemini-3.6-flash')
                    
                    with st.spinner("AI가 동선을 계산 중입니다..."):
                        prompt = f"여행지: {loc_clean}, 기간: {duration}, 스타일: {', '.join(style)}. 이동 동선이 효율적인 여행 코스를 상세히 작성해줘."
                        response = model.generate_content(prompt)
                        st.markdown(response.text)
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")
