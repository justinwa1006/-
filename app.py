import streamlit as st
import urllib.parse

# 1. 페이지 및 모바일 레이아웃 설정
st.set_page_config(
    page_title="TRIP LOG · 스마트 여행 가이드",
    page_icon="✈️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. Toss 스타일 UI 및 카드/토글 디자인
st.markdown("""
    <style>
    .stApp {
        background-color: #F2F4F6;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
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

    /* 상세 카드 스타일 */
    .detail-card {
        background: #FFFFFF;
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid #E5E8EB;
    }
    .place-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .place-name { font-size: 18px; font-weight: 700; color: #191F28; }
    .place-tag {
        background: #E8F3FF;
        color: #3182F6;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
    }
    .info-row {
        font-size: 14px;
        color: #4E5968;
        margin-top: 6px;
        line-height: 1.5;
    }
    .highlight {
        color: #3182F6;
        font-weight: 600;
    }
    
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        border: none !important;
        height: 42px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 상단 헤더
st.markdown("""
    <div class="app-header">
        <div class="app-title">✈️ TRIP LOG</div>
        <div class="app-subtitle">앱 안에서 바로 확인하는 맞춤 명소 정보</div>
    </div>
""", unsafe_allow_html=True)

# 사이드바 API 설정
with st.sidebar:
    st.header("⚙️ 앱 설정")
    gemini_api_key = st.text_input("Gemini API Key (선택)", type="password")

# 4. 입력창
location = st.text_input("📍 어디로 떠나시나요?", placeholder="예: 강릉, 후쿠오카, 제주, 속초")

# 앱 내부 상세 정보 데이터베이스 (도시별 맞춤 데이터)
place_data = {
    "강릉": {
        "🍽️ 맛집": [
            {
                "name": "동화가든",
                "tag": "짬뽕순두부 원조",
                "menu": "원조짬뽕순두부, 안송자청국장",
                "reason": "불향 가득한 매콤한 짬뽕 국물에 고소한 순두부가 조화로운 강릉 대표 맛집입니다.",
                "tip": "아침 일찍 방문하거나 테이블링 앱을 활용한 캐치테이블 예약 필수!"
            },
            {
                "name": "엄지네포장마차",
                "tag": "꼬막비빔밥",
                "menu": "꼬막무침비빔밥, 육사시미",
                "reason": "신선한 꼬막과 양념장의 감칠맛이 일품인 양 많고 푸짐한 로컬 맛집입니다.",
                "tip": "포장이 매우 빠르므로 숙소에서 편하게 먹는 것도 좋은 방법입니다."
            }
        ],
        "☕ 카페": [
            {
                "name": "툇마루",
                "tag": "시그니처 라떼",
                "menu": "툇마루 커피 (흑임자 라떼)",
                "reason": "진한 흑임자 크림과 에스프레소의 고소함이 완벽한 균형을 이루는 시그니처 카페입니다.",
                "tip": "대기 시간이 길 수 있으니 오픈 시간에 맞춰 방문하는 것을 추천합니다."
            },
            {
                "name": "테라로사 커피공장",
                "tag": "대형 핸드드립",
                "menu": "드립커피, 피칸파이, 티라미수",
                "reason": "붉은 벽돌의 웅장한 인테리어와 핸드드립 전문 원두를 즐길 수 있는 문화 공간입니다.",
                "tip": "야외 정원 및 아트숍 구경도 함께 즐기기 좋습니다."
            }
        ],
        "📸 관광지": [
            {
                "name": "경포해변 & 경포호",
                "tag": "자연/산책",
                "menu": "자전거 대여, 해변 산책",
                "reason": "시원한 동해 바다와 송림 산책로가 길게 이어져 산책하기 가장 좋은 대표 해변입니다.",
                "tip": "경포호수 둘레길에서 2인용 자전거를 타는 코스를 추천합니다."
            },
            {
                "name": "하슬라아트월드",
                "tag": "포토스팟/미술관",
                "menu": "야외 조각공원, 동굴 포토존",
                "reason": "바다가 보이는 탁 트인 전경과 창의적인 미술 작품을 배경으로 사진 찍기 좋은 곳입니다.",
                "tip": "동굴 포토존은 줄이 길 수 있으니 입장 직후 먼저 방문해보세요."
            }
        ],
        "🌙 야경": [
            {
                "name": "안목해변 커피거리",
                "tag": "해변 야경",
                "menu": "밤바다 산책, 오션뷰 카페",
                "reason": "밤이 되면 잔잔한 조명과 파도 소리가 어우러져 조용히 밤바다를 즐기기 좋습니다.",
                "tip": "창가 자리가 있는 2, 3층 카페에서 야경을 관람해보세요."
            }
        ]
    }
}

if location:
    loc_clean = location.strip()
    
    tab_recommend, tab_ai_planner = st.tabs(["✨ 명소 상세 안내", "🤖 AI 동선 플래너"])
    
    # ---------- 탭 1: 앱 내 상세 정보 제공 ----------
    with tab_recommend:
        st.write("")
        sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs(["🍽️ 맛집", "☕ 카페", "📸 관광지", "🌙 야경"])
        
        categories = [
            (sub_tab1, "🍽️ 맛집"),
            (sub_tab2, "☕ 카페"),
            (sub_tab3, "📸 관광지"),
            (sub_tab4, "🌙 야경")
        ]
        
        # 입력된 도시 데이터 확인 (없을 경우 기본 가이드 제공)
        city_data = place_data.get(loc_clean, None)
        
        for tab, cat_key in categories:
            with tab:
                st.write("")
                if city_data and cat_key in city_data:
                    for item in city_data[cat_key]:
                        # 앱 안에서 바로 보이는 상세 정보 카드
                        st.markdown(f"""
                            <div class="detail-card">
                                <div class="place-header">
                                    <span class="place-name">{item['name']}</span>
                                    <span class="place-tag">{item['tag']}</span>
                                </div>
                                <div class="info-row"><b>🍴 대표 메뉴/특징:</b> {item['menu']}</div>
                                <div class="info-row"><b>💡 추천 이유:</b> {item['reason']}</div>
                                <div class="info-row"><span class="highlight">📌 방문 꿀팁:</span> {item['tip']}</div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    # 데이터베이스에 없는 신규 지역일 경우 AI 기반 요약 가이드 제공
                    st.markdown(f"""
                        <div class="detail-card">
                            <div class="place-header">
                                <span class="place-name">📍 {loc_clean} {cat_key} 추천 가이드</span>
                            </div>
                            <div class="info-row"><b>💡 추천 요약:</b> {loc_clean} 지역의 인기 {cat_key} 명소를 탐색합니다.</div>
                            <div class="info-row">상단 <b>'🤖 AI 동선 플래너'</b> 탭을 활용하시면 {loc_clean}의 실시간 상세 코스를 한눈에 확인하실 수 있습니다.</div>
                        </div>
                    """, unsafe_allow_html=True)

    # ---------- 탭 2: AI 플래너 ----------
    with tab_ai_planner:
        st.write("")
        st.subheader("🤖 AI 맞춤 동선 설계")
        
        duration = st.selectbox("여행 기간", ["당일치기", "1박 2일", "2박 3일", "3박 4일"])
        style = st.multiselect("여행 스타일", ["맛집 탐방", "감성 카페", "자연/힐링", "액티비티"], default=["맛집 탐방", "자연/힐링"])
        
        if st.button("✨ 상세 동선 코스 생성하기", use_container_width=True):
            if not gemini_api_key:
                st.info("API Key가 설정되지 않아 샘플 코스를 출력합니다.")
                st.markdown(f"""
                ### 🗓️ {loc_clean} {duration} 추천 요약 코스
                * **오전:** {loc_clean} 도착 및 대표 관광지 탐방
                * **점심:** 대표 로컬 향토 음식 맛집 방문
                * **오후:** 뷰가 좋은 카페에서 휴식 및 주변 산책
                * **저녁:** 대표 야경 스팟 관람 후 일정 마무리
                """)
            else:
                try:
                    from google import genai
                    client = genai.Client(api_key=gemini_api_key)
                    
                    with st.spinner("AI가 동선을 계산하여 코스를 생성하는 중입니다..."):
                        prompt = f"여행지: {loc_clean}, 기간: {duration}, 스타일: {', '.join(style)}. 이동 동선과 장소별 추천 이유, 대표 메뉴를 포함해 작성해줘."
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt
                        )
                        st.markdown(response.text)
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")
