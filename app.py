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

# 2. 세션 스테이트 초기화
if "itinerary" not in st.session_state:
    st.session_state.itinerary = []
if "schedule_plan" not in st.session_state:
    st.session_state.schedule_plan = ""

# 3. 여행 감성 커스텀 CSS
st.markdown("""
    <style>
    /* --------------------------------------------------
       테마 변수 설정 (라이트 / 다크)
    -------------------------------------------------- */
    :root {
        --bg-color: #F8FAFC;
        --card-bg: #FFFFFF;
        --card-border: #E2E8F0;
        --text-primary: #0F172A;
        --text-secondary: #64748B;
        --text-address: #334155;
        --badge-bg: #E0F2FE;
        --badge-text: #0369A1;
        --chip-bg: #F1F5F9;
        --chip-active: #2563EB;
        --chip-active-text: #FFFFFF;
        --plan-bg: #F0F9FF;
        --plan-border: #BAE6FD;
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --bg-color: #0F172A;
            --card-bg: #1E293B;
            --card-border: #334155;
            --text-primary: #F8FAFC;
            --text-secondary: #94A3B8;
            --text-address: #CBD5E1;
            --badge-bg: #0369A1;
            --badge-text: #E0F2FE;
            --chip-bg: #334155;
            --chip-active: #3B82F6;
            --chip-active-text: #FFFFFF;
            --plan-bg: #0F172A;
            --plan-border: #1E3A8A;
        }
    }

    /* --------------------------------------------------
       상단 여행 히어로 배너
    -------------------------------------------------- */
    .hero-container {
        background: linear-gradient(135deg, #0284C7 0%, #2563EB 50%, #4F46E5 100%);
        padding: 28px 24px;
        border-radius: 20px;
        color: #FFFFFF !important;
        margin-bottom: 24px;
        box-shadow: 0 12px 20px -5px rgba(37, 99, 235, 0.3);
        text-align: center;
    }
    .hero-title {
        font-size: 24px;
        font-weight: 900;
        letter-spacing: -0.5px;
        margin: 0;
        color: #FFFFFF !important;
    }
    .hero-subtitle {
        font-size: 13px;
        color: #E0F2FE !important;
        margin-top: 8px;
        font-weight: 500;
    }

    /* --------------------------------------------------
       대분류 라디오 버튼 ➔ 여행 감성 칩(Chip) 커스텀
    -------------------------------------------------- */
    div[data-testid="stRadio"] > label {
        display: none !important; /* 기본 라디오 헤더 숨기기 */
    }
    div[data-testid="stRadio"] > div {
        display: flex;
        flex-direction: row;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 12px;
    }
    div[data-testid="stRadio"] label {
        background-color: var(--card-bg) !important;
        border: 1.5px solid var(--card-border) !important;
        border-radius: 12px !important;
        padding: 10px 16px !important;
        cursor: pointer;
        transition: all 0.2s ease-in-out;
        font-weight: 600 !important;
        font-size: 14px !important;
        color: var(--text-primary) !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    div[data-testid="stRadio"] label:hover {
        border-color: #3B82F6 !important;
        transform: translateY(-2px);
    }

    /* --------------------------------------------------
       장소 추천 카드 스타일
    -------------------------------------------------- */
    .place-card {
        background-color: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 16px;
        padding: 18px 20px;
        margin-bottom: 14px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .place-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.06);
    }
    .place-badge {
        display: inline-block;
        background-color: var(--badge-bg);
        color: var(--badge-text);
        font-size: 11px;
        font-weight: 800;
        padding: 3px 10px;
        border-radius: 20px;
        margin-bottom: 8px;
        letter-spacing: 0.5px;
    }
    .place-title {
        font-size: 17px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 4px;
    }
    .place-category {
        font-size: 12px;
        color: var(--text-secondary);
        margin-bottom: 8px;
        font-weight: 500;
    }
    .place-address {
        font-size: 13px;
        color: var(--text-address);
        margin-bottom: 12px;
    }
    .map-btn {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background-color: #03C75A;
        color: #FFFFFF !important;
        font-size: 12px;
        font-weight: 700;
        padding: 7px 14px;
        border-radius: 8px;
        text-decoration: none !important;
        box-shadow: 0 2px 6px rgba(3, 199, 90, 0.2);
    }

    /* 일정 박스 스타일 */
    .plan-box {
        background-color: var(--plan-bg);
        border: 1px solid var(--plan-border);
        border-radius: 16px;
        padding: 22px;
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

# 5. 상단 헤더
st.markdown("""
    <div class="hero-container">
        <div class="hero-title">✈️ TRIP LOG</div>
        <div class="hero-subtitle">나만의 실시간 여행 가이드 & 최적 동선 플래너</div>
    </div>
""", unsafe_allow_html=True)

def clean_html(text):
    return re.sub(r'<[^>]+>', '', text)

# 6. 파이썬 자체 동선 정렬 함수
def generate_smart_schedule(itinerary_list):
    meals, cafes, spots, nights, others = [], [], [], [], []

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

    if spots:
        schedule.append(("10:00 - 12:00 [오전 관광]", spots.pop(0)))
    elif cafes:
        schedule.append(("10:30 - 12:00 [오전 티타임]", cafes.pop(0)))

    if meals:
        schedule.append(("12:30 - 14:00 [점심 식사]", meals.pop(0)))

    if cafes:
        schedule.append(("14:30 - 16:00 [디저트 & 카페]", cafes.pop(0)))

    if spots:
        schedule.append(("16:00 - 18:00 [오후 관광]", spots.pop(0)))

    if meals:
        schedule.append(("18:30 - 20:00 [저녁 식사]", meals.pop(0)))

    if nights:
        schedule.append(("20:30 - 21:30 [야경 코스]", nights.pop(0)))

    remaining = spots + meals + cafes + nights + others
    for rem in remaining:
        schedule.append(("자유 방문 추천 장소", rem))

    plan_md = "### 🗺️ 추천 최적 여행 동선\n\n"
    for time_slot, place in schedule:
        plan_md += f"**{time_slot}**  \n"
        plan_md += f"└ 📍 **{place['title']}** (`{place['category']}`)  \n"
        plan_md += f"   *주소: {place['address']}*  \n\n"

    return plan_md

# 7. 탭 구성
tab1, tab2 = st.tabs(["🧭 장소 탐색", f"🗓️ 나의 일정표 ({len(st.session_state.itinerary)})"])

# -------------------------------------------------------------
# TAB 1: 장소 검색 & 결과
# -------------------------------------------------------------
with tab1:
    location = st.text_input("📍 떠나실 목적지를 입력하세요", value="", placeholder="예: 제주도, 강릉, 속초, 부산, 여수")

    st.write("**카테고리 선택**")
    # 트렌디한 카드 스타일로 커스텀된 대분류 라디오 버튼
    category = st.radio(
        "대분류 선택", 
        ["🍽️ 맛집", "☕ 카페", "🏞️ 관광지", "🌙 야경"],
        horizontal=True,
        label_visibility="collapsed"
    )

    subcategory = "전체"
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
                    st.markdown(f"#### 🔍 **{location}** 인기 {query.replace(location, '').strip()} TOP {len(items)}")
                    
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
# TAB 2: 담은 일정 & 동선 생성
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
        st.subheader("⚡ 1초 자동 동선 정렬")
        st.caption("장소 성격(맛집, 카페, 관광지, 야경)에 맞춰 가장 효율적인 시간대별 동선을 짜드립니다.")
        
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
        st.info("💡 **'🧭 장소 탐색'** 탭에서 마음에 드는 장소의 **'➕ 일정에 담기'** 버튼을 눌러 나만의 코스를 담아보세요!")
