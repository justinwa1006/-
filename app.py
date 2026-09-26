import streamlit as st
import requests
import re
import urllib.parse

# -------------------------------------------------------------
# 1. 페이지 레이아웃 설정
# -------------------------------------------------------------
st.set_page_config(
    page_title="TRIP LOG · 여행 가이드",
    page_icon="✈️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------------------
# 2. 세션 스테이트 초기화
# -------------------------------------------------------------
if "itinerary" not in st.session_state:
    st.session_state.itinerary = []
if "schedule_plan" not in st.session_state:
    st.session_state.schedule_plan = ""

# -------------------------------------------------------------
# 3. 여행 감성 커스텀 CSS (히어로 배너, 대분류 칩, 버튼)
# -------------------------------------------------------------
st.markdown("""
    <style>
    /* 히어로 배너 */
    .hero-container {
        background: linear-gradient(135deg, #0284C7 0%, #2563EB 50%, #4F46E5 100%);
        padding: 24px;
        border-radius: 18px;
        color: #FFFFFF !important;
        margin-bottom: 20px;
        box-shadow: 0 10px 18px -5px rgba(37, 99, 235, 0.3);
        text-align: center;
    }
    .hero-title {
        font-size: 24px;
        font-weight: 900;
        margin: 0;
        color: #FFFFFF !important;
    }
    .hero-subtitle {
        font-size: 13px;
        color: #E0F2FE !important;
        margin-top: 6px;
    }

    /* 대분류 라디오 ➔ 여행 칩(Chip) 커스텀 */
    div[data-testid="stRadio"] > label { display: none !important; }
    div[data-testid="stRadio"] > div {
        display: flex;
        flex-direction: row;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 12px;
    }
    div[data-testid="stRadio"] label {
        border-radius: 12px !important;
        padding: 8px 14px !important;
        cursor: pointer;
        font-weight: 600 !important;
        font-size: 14px !important;
    }

    /* 네이버 지도 버튼 */
    .map-btn {
        display: inline-flex;
        align-items: center;
        background-color: #03C75A;
        color: #FFFFFF !important;
        font-size: 13px;
        font-weight: 700;
        padding: 6px 14px;
        border-radius: 8px;
        text-decoration: none !important;
    }

    /* 일정 출력 박스 */
    .plan-box {
        background-color: rgba(3, 105, 161, 0.05);
        border: 1px solid rgba(3, 105, 161, 0.2);
        border-radius: 16px;
        padding: 20px;
        margin-top: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 4. API 인증 설정 (Secrets 우선 적용)
# -------------------------------------------------------------
client_id = st.secrets.get("NAVER_CLIENT_ID", "")
client_secret = st.secrets.get("NAVER_CLIENT_SECRET", "")

if not client_id or not client_secret:
    with st.sidebar:
        st.subheader("⚙️ API 인증 설정")
        client_id = st.text_input("Naver Client ID", type="password")
        client_secret = st.text_input("Naver Client Secret", type="password")

# -------------------------------------------------------------
# 5. 상단 헤더
# -------------------------------------------------------------
st.markdown("""
    <div class="hero-container">
        <div class="hero-title">✈️ TRIP LOG</div>
        <div class="hero-subtitle">나만의 실시간 여행 가이드 & 최적 동선 플래너</div>
    </div>
""", unsafe_allow_html=True)

def clean_html(text):
    return re.sub(r'<[^>]+>', '', text)

# 고화질 대표 예비 이미지
DEFAULT_IMAGES = {
    "🍽️ 맛집": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=600&q=80",
    "☕ 카페": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=600&q=80",
    "🏞️ 관광지": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600&q=80",
    "🌙 야경": "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=600&q=80"
}

# -------------------------------------------------------------
# 6. API 캐싱 처리 함수
# -------------------------------------------------------------
@st.cache_data(ttl=3600)
def fetch_naver_search(query, c_id, c_secret):
    """장소 검색 API (1시간 캐싱)"""
    url = "https://naverapihub.apigw.ntruss.com/search/v1/local"
    headers = {"X-NCP-APIGW-API-KEY-ID": c_id, "X-NCP-APIGW-API-KEY": c_secret}
    params1 = {"query": query, "display": 5, "start": 1, "sort": "comment"}
    params2 = {"query": query, "display": 5, "start": 6, "sort": "comment"}
    items = []
    try:
        res1 = requests.get(url, headers=headers, params=params1)
        res2 = requests.get(url, headers=headers, params=params2)
        if res1.status_code == 200:
            items.extend(res1.json().get("items", []))
        if res2.status_code == 200:
            items.extend(res2.json().get("items", []))
    except Exception:
        pass
    return items

@st.cache_data(ttl=3600)
def get_place_images(location_name, place_title, category_key, c_id, c_secret, display_count=3):
    """이미지 검색 API (인기 사진 3장 가져오기)"""
    url = "https://naverapihub.apigw.ntruss.com/search/v1/image"
    headers = {"X-NCP-APIGW-API-KEY-ID": c_id, "X-NCP-APIGW-API-KEY": c_secret}
    params = {"query": f"{location_name} {place_title}", "display": display_count, "sort": "sim"}
    img_list = []
    try:
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            items = res.json().get("items", [])
            for item in items:
                link = item.get("link") or item.get("thumbnail")
                if link:
                    img_list.append(link)
    except Exception:
        pass

    fallback_img = DEFAULT_IMAGES.get(category_key, DEFAULT_IMAGES["🏞️ 관광지"])
    while len(img_list) < display_count:
        img_list.append(fallback_img)

    return img_list[:display_count]

# -------------------------------------------------------------
# 7. 최적 동선 정렬 함수
# -------------------------------------------------------------
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

# -------------------------------------------------------------
# 8. 탭 구성
# -------------------------------------------------------------
tab1, tab2 = st.tabs(["🧭 장소 탐색", f"🗓️ 나의 일정표 ({len(st.session_state.itinerary)})"])

# -------------------------------------------------------------
# TAB 1: 장소 검색 & 네이버 플레이스 스타일 카드
# -------------------------------------------------------------
with tab1:
    location = st.text_input("📍 떠나실 목적지를 입력하세요", value="", placeholder="예: 제주도, 강릉, 속초, 부산, 여수")

    st.write("**카테고리 선택**")
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
            st.info("💡 사이드바 또는 Streamlit Secrets에 Naver API Key를 설정해 주세요.")
        else:
            clean_category = category.split()[-1]
            query = f"{location} {subcategory}" if subcategory != "전체" else f"{location} {clean_category}"
            
            items = fetch_naver_search(query, client_id, client_secret)
            
            if items:
                st.write("")
                st.markdown(f"#### 🔍 **{location}** 인기 {query.replace(location, '').strip()} TOP {len(items)}")
                
                for idx, item in enumerate(items, 1):
                    title = clean_html(item.get("title", ""))
                    address = item.get("roadAddress") or item.get("address", "")
                    cat = item.get("category", "")
                    
                    img_urls = get_place_images(location, title, category, client_id, client_secret, display_count=3)
                    map_query = urllib.parse.quote(f"{location} {title}")
                    map_url = f"https://map.naver.com/v5/search/{map_query}"
                    
                    # 네이버 플레이스 스타일 카드 컨테이너
                    with st.container(border=True):
                        # 📸 3분할 대표 이미지 그리드 (메인 1장 + 서브 2장)
                        img_cols = st.columns([2, 1, 1])
                        for c_idx, col in enumerate(img_cols):
                            with col:
                                if c_idx < len(img_urls):
                                    st.image(img_urls[c_idx], use_container_width=True)
                        
                        st.write("")
                        st.markdown(f"### **{idx}. {title}**")
                        st.caption(f"🏷️ **{cat}** | 📍 {address}")
                        
                        col_map, col_add = st.columns([1.5, 1])
                        with col_map:
                            st.markdown(f'<a href="{map_url}" target="_blank" class="map-btn">🗺️ 네이버 지도로 위치 확인 ↗</a>', unsafe_allow_html=True)
                        with col_add:
                            place_info = {"title": title, "address": address, "category": cat}
                            if st.button(f"➕ 일정에 담기", key=f"add_{idx}_{title}"):
                                if place_info not in st.session_state.itinerary:
                                    st.session_state.itinerary.append(place_info)
                                    st.toast(f"✅ '{title}' 일정에 추가되었습니다!")
                                    st.rerun()
                                else:
                                    st.toast(f"⚠️ 이미 담긴 장소입니다.")
            else:
                st.warning("검색 결과가 없습니다.")

# -------------------------------------------------------------
# TAB 2: 담은 일정 & 1초 동선 생성
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
