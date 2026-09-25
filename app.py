import streamlit as st
import requests
import re
import urllib.parse

# 1. 페이지 레이아웃 설정
st.set_page_config(
    page_title="TRIP LOG · 여행 가이드",
    page_icon="✈️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. 세션 스테이트 초기화 (담은 일정 & 생성된 동선 저장용)
if "itinerary" not in st.session_state:
    st.session_state.itinerary = []
if "schedule_plan" not in st.session_state:
    st.session_state.schedule_plan = ""

# 3. 커스텀 CSS (반응형 다크/라이트 테마 + 카드/상자 디자인)
st.markdown("""
    <style>
    :root {
        --card-bg: #FFFFFF;
        --card-border: #E2E8F0;
        --text-primary: #0F172A;
        --text-secondary: #64748B;
        --text-address: #334155;
        --badge-bg: #EFF6FF;
        --badge-text: #1D4ED8;
        --plan-bg: #F0F9FF;
        --plan-border: #BAE6FD;
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --card-bg: #1E293B;
            --card-border: #334155;
            --text-primary: #F8FAFC;
            --text-secondary: #94A3B8;
            --text-address: #CBD5E1;
            --badge-bg: #1E3A8A;
            --badge-text: #93C5FD;
            --plan-bg: #0F172A;
            --plan-border: #1E3A8A;
        }
    }

    .hero-container {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 24px 20px;
        border-radius: 16px;
        color: #FFFFFF !important;
        margin-bottom: 20px;
        box-shadow: 0 10px 15px -3px rgba(30, 58, 138, 0.2);
    }
    .hero-title {
        font-size: 22px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        color: #FFFFFF !important;
    }
    .hero-subtitle {
        font-size: 13px;
        color: #E0E7FF !important;
        margin-top: 6px;
    }

    .place-card {
        background-color: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }
    .place-badge {
        display: inline-block;
        background-color: var(--badge-bg);
        color: var(--badge-text);
        font-size: 11px;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    .place-title {
        font-size: 16px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 4px;
    }
    .place-category {
        font-size: 12px;
        color: var(--text-secondary);
        margin-bottom: 8px;
    }
    .place-address {
        font-size: 13px;
        color: var(--text-address);
        margin-bottom: 12px;
    }
    .map-btn {
        display: inline-flex;
        align-items: center;
        background-color: #03C75A;
        color: #FFFFFF !important;
        font-size: 12px;
        font-weight: 600;
        padding: 6px 12px;
        border-radius: 6px;
        text-decoration: none !important;
    }
    .plan-box {
        background-color: var(--plan-bg);
        border: 1px solid var(--plan-border);
        border-radius: 12px;
        padding: 20px;
        margin-top: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# 4. 사이드바 설정
with st.sidebar:
    st.subheader("⚙️ API 인증 설정")
    client_id = st.text_input("Naver Client ID", type="password")
    client_secret = st.text_input("Naver Client Secret", type="password")
    st.caption("NAVER API HUB에서 발급받은 인증키를 입력해주세요.")

# 5. 상단 배너 헤더
st.markdown("""
    <div class="hero-container">
        <div class="hero-title">✈️ TRIP LOG</div>
        <div class="hero-subtitle">네이버 실시간 데이터 기반 맞춤 여행 가이드</div>
    </div>
""", unsafe_allow_html=True)

def clean_html(text):
    return re.sub(r'<[^>]+>', '', text)

# 6. 파이썬 규칙 기반(Rule-based) 동선 자동 정렬 함수 (2번 방안)
def generate_smart_schedule(itinerary_list):
    meals, cafes, spots, nights, others = [], [], [], [], []

    # 카테고리 태그 분류
    for item in itinerary_list:
        cat = item.get("category", "")
        if any(k in cat for k in ["음식점", "한식", "양식", "일식", "중식", "고기", "해산물", "뷔페", "분식"]):
            meals.append(item)
        elif any(k in cat for k in ["카페", "디저트", "베이커리", "차"]):
            cafes.append(item)
        elif any(k in cat for k in ["야경", "전망대", "전망"]):
            nights.append(item)
        elif any(k in cat for k in ["관광", "명소", "공원", "해수욕장", "테마파크", "박물관"]):
            spots.append(item)
        else:
            others.append(item)

    schedule = []

    # 10:00 (오전 관광 또는 카페)
    if spots:
        schedule.append(("10:00 - 12:00 [오전 관광]", spots.pop(0)))
    elif cafes:
        schedule.append(("10:30 - 12:00 [오전 티타임]", cafes.pop(0)))

    # 12:30 (점심 식사)
    if meals:
        schedule.append(("12:30 - 14:00 [점심 식사]", meals.pop(0)))

    # 14:30 (디저트 & 카페)
    if cafes:
        schedule.append(("14:30 - 16:00 [디저트 & 카페]", cafes.pop(0)))

    # 16:00 (오후 관광)
    if spots:
        schedule.append(("16:00 - 18:00 [오후 관광]", spots.pop(0)))

    # 18:30 (저녁 식사)
    if meals:
        schedule.append(("18:30 - 20:00 [저녁 식사]", meals.pop(0)))

    # 20:30 (야경)
    if nights:
        schedule.append(("20:30 - 21:30 [야경 코스]", nights.pop(0)))

    # 남은 장소들 처리
    remaining = spots + meals + cafes + nights + others
    for rem in remaining:
        schedule.append(("자유 방문 추천 장소", rem))

    # 마크다운 일정표 생성
    plan_md = "### 🗓️ 추천 최적 동선 일정표\n\n"
    for time_slot, place in schedule:
        plan_md += f"**{time_slot}**  \n"
        plan_md += f"└ 📍 **{place['title']}** (`{place['category']}`)  \n"
        plan_md += f"   *주소: {place['address']}*  \n\n"

    return plan_md

# 7. 탭(Tab)으로 UI 분리
tab1, tab2 = st.tabs(["🔍 장소 검색", f"🗓️ 나의 여행 일정표 ({len(st.session_state.itinerary)})"])

# -------------------------------------------------------------
# TAB 1: 장소 검색 & 결과 출력
# -------------------------------------------------------------
with tab1:
    location = st.text_input("📍 어디로 떠나시나요?", value="", placeholder="예: 제주도, 강릉, 속초, 부산, 여수")

    col1, col2 = st.columns([1, 1])
    with col1:
        category = st.radio("대분류 선택", ["🍽️ 맛집", "☕ 카페", "🏞️ 관광지", "🌙 야경"])

    subcategory = "전체"
    with col2:
        if category == "🍽️ 맛집":
            subcategory = st.selectbox("🍽️ 맛집 세부 종류", ["전체", "한식", "양식", "일식", "중식", "고기/구이", "해산물/회", "분식/간편식"])
        elif category == "☕ 카페":
            subcategory = st.selectbox("☕ 카페 세부 종류", ["전체", "디저트/베이커리", "뷰맛집", "대형카페", "감성카페"])

    if location:
        if not client_id or not client_secret:
            st.info("💡 왼쪽 사이드바에 Naver API Client ID와 Secret을 입력해 주세요.")
        else:
            url = "https://naverapihub.apigw.ntruss.com/search/v1/local"
            headers = {
                "X-NCP-APIGW-API-KEY-ID": client_id,
                "X-NCP-APIGW-API-KEY": client_secret
            }
            
            clean_category = category.split()[-1]
            query = f"{location} {subcategory}" if subcategory != "전체" else f"{location} {clean_category}"
            
            params1 = {"query": query, "display": 5, "start": 1, "sort": "comment"}
            params2 = {"query": query, "display": 5, "start": 6, "sort": "comment"}

            try:
                res1 = requests.get(url, headers=headers, params=params1)
                res2 = requests.get(url, headers=headers, params=params2)
                
                items = []
                if res1.status_code == 200:
                    items.extend(res1.json().get("items", []))
                if res2.status_code == 200:
                    items.extend(res2.json().get("items", []))
                    
                if items:
                    st.write("")
                    st.markdown(f"#### 🔍 **{location}** 추천 {query.replace(location, '').strip()} TOP {len(items)}")
                    
                    for idx, item in enumerate(items, 1):
                        title = clean_html(item.get("title", ""))
                        address = item.get("roadAddress") or item.get("address", "")
                        cat = item.get("category", "")
                        
                        map_query = urllib.parse.quote(f"{location} {title}")
                        map_url = f"https://map.naver.com/v5/search/{map_query}"
                        
                        st.markdown(f"""
                            <div class="place-card">
                                <span class="place-badge">TOP {idx}</span>
                                <div class="place-title">{title}</div>
                                <div class="place-category">🏷️ {cat}</div>
                                <div class="place-address">📍 {address}</div>
                                <a href="{map_url}" target="_blank" class="map-btn">
                                    네이버 지도로 위치 확인 ↗
                                </a>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        place_info = {"title": title, "address": address, "category": cat}
                        if st.button(f"➕ '{title}' 일정에 담기", key=f"add_{idx}_{title}"):
                            if place_info not in st.session_state.itinerary:
                                st.session_state.itinerary.append(place_info)
                                st.toast(f"✅ '{title}' 장소가 일정표에 추가되었습니다!")
                                st.rerun()
                            else:
                                st.toast(f"⚠️ 이미 일정에 담긴 장소입니다.")
                else:
                    st.warning("검색 결과가 없습니다.")
            except Exception as e:
                st.error(f"요청 중 오류가 발생했습니다: {e}")

# -------------------------------------------------------------
# TAB 2: 담은 일정 관리 & 1초 동선 자동 정렬
# -------------------------------------------------------------
with tab2:
    if st.session_state.itinerary:
        st.subheader("📋 선택한 장소 목록")
        
        itinerary_text = ""
        for i, place in enumerate(st.session_state.itinerary, 1):
            col_item, col_del = st.columns([5, 1])
            with col_item:
                st.write(f"**{i}. {place['title']}** (`{place['category']}`)")
                st.caption(f"📍 {place['address']}")
            with col_del:
                if st.button("삭제", key=f"del_{i}"):
                    st.session_state.itinerary.pop(i - 1)
                    st.rerun()
            itinerary_text += f"{i}. {place['title']} ({place['category']}) - {place['address']}\n"
        
        st.write("")
        if st.button("🗑️ 일정 전체 비우기"):
            st.session_state.itinerary = []
            st.session_state.schedule_plan = ""
            st.rerun()

        st.write("---")
        st.subheader("⚡ 1초 자동 동선 정렬 (무제한/100% 무료)")
        st.caption("외부 AI/API 없이 장소 성격(맛집, 카페, 관광지, 야경)에 맞게 최적의 동선을 생성합니다.")
        
        if st.button("🚀 시간대별 자동 일정표 생성하기"):
            st.session_state.schedule_plan = generate_smart_schedule(st.session_state.itinerary)
            st.success("🎉 최적 동선 일정표 생성이 완료되었습니다!")

        if st.session_state.schedule_plan:
            st.markdown('<div class="plan-box">', unsafe_allow_html=True)
            st.markdown(st.session_state.schedule_plan)
            st.markdown('</div>', unsafe_allow_html=True)

        st.write("---")
        st.text_area("📋 일정 텍스트 복사 (카톡/메모장 공유용)", value=itinerary_text, height=120)

    else:
        st.info("💡 **'🔍 장소 검색'** 탭에서 마음에 드는 장소의 **'➕ 일정에 담기'** 버튼을 눌러 나만의 코스를 담아보세요!")
