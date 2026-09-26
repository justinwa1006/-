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
# 3. 여행 감성 커스텀 CSS (다크모드 완벽 대응 + 고화질 피드)
# -------------------------------------------------------------
st.markdown("""
    <!-- 외부 이미지 리퍼러 보안 차단 해제 -->
    <meta name="referrer" content="no-referrer">

    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    * {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
    }

    /* 히어로 배너 */
    .hero-container {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 50%, #4834D4 100%);
        padding: 28px 20px;
        border-radius: 22px;
        color: #FFFFFF !important;
        margin-bottom: 24px;
        box-shadow: 0 12px 28px -6px rgba(255, 107, 107, 0.35);
        text-align: center;
    }
    .hero-title {
        font-size: 26px;
        font-weight: 900;
        letter-spacing: -0.5px;
        margin: 0;
        color: #FFFFFF !important;
    }
    .hero-subtitle {
        font-size: 13px;
        color: #FFEAA7 !important;
        margin-top: 6px;
        font-weight: 500;
    }

    /* 🏷️ 다크모드 대응 카테고리 칩 (stRadio) */
    div[data-testid="stRadio"] > label { display: none !important; }
    div[data-testid="stRadio"] > div {
        display: flex;
        flex-direction: row;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 12px;
    }
    div[data-testid="stRadio"] label {
        border-radius: 20px !important;
        padding: 8px 18px !important;
        cursor: pointer;
        font-weight: 600 !important;
        font-size: 14px !important;
        border: 1px solid #334155 !important;
        background: #1E293B !important;
        color: #F8FAFC !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] label span {
        color: #F8FAFC !important;
        font-weight: 600 !important;
    }
    div[data-testid="stRadio"] label:hover {
        background: #334155 !important;
        border-color: #64748B !important;
    }

    /* 📸 카드 컨테이너 (다크/라이트 호환 스타일) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.25) !important;
        background: #18181B !important;
        padding: 18px !important;
        margin-bottom: 18px !important;
    }

    /* 🖼️ 1:1 정사각형 고화질 인스타 피드 그리드 */
    div[data-testid="stColumn"] div[data-testid="stImage"] {
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3) !important;
        background-color: #27272A !important;
    }

    div[data-testid="stColumn"] div[data-testid="stImage"] img {
        aspect-ratio: 1 / 1 !important;
        width: 100% !important;
        height: auto !important;
        object-fit: cover !important;
        border-radius: 12px !important;
        transition: transform 0.3s ease, filter 0.3s ease !important;
    }

    /* 인스타 피드 호버 효과 */
    div[data-testid="stColumn"] div[data-testid="stImage"]:hover img {
        transform: scale(1.06) !important;
        filter: brightness(1.05) !important;
    }

    /* 🔍 전체화면(확대) 클릭 시 원본 비율 복원 */
    div[data-testid="stStyledFullScreenFrame"] img,
    div[role="dialog"] img,
    div[data-testid="stModal"] img,
    div[data-baseweb="modal"] img {
        aspect-ratio: auto !important;
        height: auto !important;
        max-height: 85vh !important;
        width: auto !important;
        max-width: 90vw !important;
        object-fit: contain !important;
        border-radius: 8px !important;
    }

    /* 감성 뱃지 & 해시태그 스타일 */
    .tag-badge {
        display: inline-block;
        background: #27272A;
        color: #E4E4E7;
        font-size: 12px;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 8px;
        margin-right: 6px;
        border: 1px solid #3F3F46;
    }

    /* 네이버 지도 버튼 */
    .map-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background-color: #03C75A;
        color: #FFFFFF !important;
        font-size: 13px;
        font-weight: 700;
        padding: 8px 16px;
        border-radius: 10px;
        text-decoration: none !important;
        box-shadow: 0 4px 10px rgba(3, 199, 90, 0.25);
        transition: transform 0.15s ease;
    }
    .map-btn:hover {
        transform: translateY(-1px);
    }

    /* 일정 출력 박스 */
    .plan-box {
        background-color: #18181B;
        border: 1px solid #27272A;
        border-radius: 18px;
        padding: 22px;
        margin-top: 16px;
        color: #F4F4F5;
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
        <div class="hero-title">✨ TRIP LOG</div>
        <div class="hero-subtitle">인스타 감성 핫플 탐색 & 스마트 감성 코스 플래너</div>
    </div>
""", unsafe_allow_html=True)

def clean_html(text):
    return re.sub(r'<[^>]+>', '', text)

# 고화질 백업 이미지 목록
DEFAULT_IMAGES = {
    "🍽️ 맛집": [
        "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=1000&q=85",
        "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=1000&q=85",
        "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=1000&q=85"
    ],
    "☕ 카페": [
        "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=1000&q=85",
        "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=1000&q=85",
        "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=1000&q=85"
    ],
    "🏞️ 관광지": [
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1000&q=85",
        "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=1000&q=85",
        "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=1000&q=85"
    ],
    "🌙 야경": [
        "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=1000&q=85",
        "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=1000&q=85",
        "https://images.unsplash.com/photo-1514565131-fce0801e5785?w=1000&q=85"
    ]
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
def get_place_images(location_name, place_title, category_key, c_id, c_secret, display_count=6):
    """이미지 검색 API (고화질 원본 link 우선 가져오기)"""
    url = "https://naverapihub.apigw.ntruss.com/search/v1/image"
    headers = {"X-NCP-APIGW-API-KEY-ID": c_id, "X-NCP-APIGW-API-KEY": c_secret}
    params = {"query": f"{location_name} {place_title}", "display": display_count * 2, "sort": "sim"}
    img_list = []
    try:
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            items = res.json().get("items", [])
            for item in items:
                # 저화질 thumbnail 대신 고화질 원본 link 적용
                link = item.get("link") or item.get("thumbnail")
                if link and link.startswith("http"):
                    img_list.append(link)
    except Exception:
        pass

    fallbacks = DEFAULT_IMAGES.get(category_key, DEFAULT_IMAGES["🏞️ 관광지"])
    fb_idx = 0
    while len(img_list) < display_count:
        img_list.append(fallbacks[fb_idx % len(fallbacks)])
        fb_idx += 1

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
tab1, tab2 = st.tabs(["🧭 감성 핫플 탐색", f"🗓️ 나의 코스 ({len(st.session_state.itinerary)})"])

# -------------------------------------------------------------
# TAB 1: 장소 검색 & 인스타 감성 피드 갤러리
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
                st.markdown(f"#### 📸 **{location}** 인기 {query.replace(location, '').strip()} TOP {len(items)}")
                
                for idx, item in enumerate(items, 1):
                    title = clean_html(item.get("title", ""))
                    address = item.get("roadAddress") or item.get("address", "")
                    cat = item.get("category", "")
                    
                    img_urls = get_place_images(location, title, category, client_id, client_secret, display_count=6)
                    map_query = urllib.parse.quote(f"{location} {title}")
                    map_url = f"https://map.naver.com/v5/search/{map_query}"
                    
                    with st.container(border=True):
                        # 🖼️ 1:1 고화질 피드 그리드 (2행 3열)
                        for row in range(2):
                            img_cols = st.columns(3)
                            for c_idx in range(3):
                                img_idx = row * 3 + c_idx
                                if img_idx < len(img_urls):
                                    img_cols[c_idx].image(img_urls[img_idx], use_container_width=True)
                        
                        st.write("")
                        st.markdown(f"### **{idx}. {title}**")
                        st.markdown(f'<span class="tag-badge">#{cat}</span> <span class="tag-badge">#{location}핫플</span>', unsafe_allow_html=True)
                        st.caption(f"📍 {address}")
                        
                        col_map, col_add = st.columns([1.5, 1])
                        with col_map:
                            st.markdown(f'<a href="{map_url}" target="_blank" class="map-btn">🟢 네이버 지도 ↗</a>', unsafe_allow_html=True)
                        with col_add:
                            place_info = {"title": title, "address": address, "category": cat}
                            if st.button(f"➕ 일정 담기", key=f"add_{idx}_{title}"):
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
        st.info("💡 **'🧭 감성 핫플 탐색'** 탭에서 마음에 드는 장소의 **'➕ 일정 담기'** 버튼을 눌러 나만의 코스를 담아보세요!")
