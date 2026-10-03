import streamlit as st
import requests
import re
import urllib.parse
from datetime import date
from supabase import create_client, Client

# Supabase 연결 설정
SUPABASE_URL = "https://wtllperjappemsnvtrfm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind0bGxwZXJqYXBwZW1zbnZ0cmZtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTEwMTY3NDYsImV4cCI6MjEwNjU5Mjc0Nn0.Yav2YOteRtoECzTp1oHEaMCwQjLt45Z_zbpGw3X1WJ8"

# 클라이언트 생성
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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
# 2. 세션 스테이트 초기화 (앱 로딩 시 최초 1회만 DB 로드)
# -------------------------------------------------------------
if "itinerary" not in st.session_state:
    st.session_state.itinerary = []
if "schedule_plan" not in st.session_state:
    st.session_state.schedule_plan = ""

if "initialized" not in st.session_state:
    st.session_state.initialized = True
    try:
        response = supabase.table("my_courses").select("*").execute()
        if response.data:
            st.session_state.itinerary = [
                {
                    "id": item.get("id"),
                    "title": item.get("title", ""),
                    "category": item.get("category", ""),
                    "address": item.get("address", ""),
                    "date": date.fromisoformat(item.get("visit_date")) if item.get("visit_date") else date.today()
                } for item in response.data
            ]
    except Exception as e:
        pass

# -------------------------------------------------------------
# 3. 커스텀 CSS (☀️ 밝은 테마 가독성 & 터치 최적화)
# -------------------------------------------------------------
st.markdown("""
    <meta name="referrer" content="no-referrer">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">

    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    * {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
        box-sizing: border-box;
    }

    /* 🚫 Streamlit 기본 상단 메뉴바 숨김 */
    header[data-testid="stHeader"] {
        display: none !important;
    }

    /* 📱 모바일 화면 여백 최적화 */
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 2rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        max-width: 500px !important;
    }
    
    /* 히어로 배너 */
    .hero-container {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 50%, #4834D4 100%);
        padding: 20px 16px;
        border-radius: 18px;
        color: #FFFFFF !important;
        margin-bottom: 16px;
        box-shadow: 0 8px 20px -4px rgba(255, 107, 107, 0.25);
        text-align: center;
    }
    .hero-title {
        font-size: 22px;
        font-weight: 900;
        letter-spacing: -0.5px;
        margin: 0;
        color: #FFFFFF !important;
    }
    .hero-subtitle {
        font-size: 12px;
        color: #FFEAA7 !important;
        margin-top: 4px;
        font-weight: 500;
        opacity: 0.95;
    }

    /* 카테고리 칩 (stRadio) */
    div[data-testid="stRadio"] > label { display: none !important; }
    div[data-testid="stRadio"] > div {
        display: flex;
        flex-direction: row;
        gap: 6px;
        flex-wrap: wrap;
        margin-bottom: 10px;
    }
    
    div[data-testid="stRadio"] label {
        flex: 1 1 calc(50% - 6px) !important;
        min-height: 44px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border-radius: 12px !important;
        padding: 8px 12px !important;
        cursor: pointer;
        font-weight: 600 !important;
        font-size: 13px !important;
        border: 1px solid #E2E8F0 !important;
        background: #F8FAFC !important;
        color: #334155 !important;
        text-align: center !important;
        transition: all 0.2s ease;
    }
    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] label span {
        color: #334155 !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }

    div[data-testid="stRadio"] label:has(input:checked) {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%) !important;
        border-color: #FF6B6B !important;
        box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3) !important;
    }
    div[data-testid="stRadio"] label:has(input:checked) p,
    div[data-testid="stRadio"] label:has(input:checked) span {
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }

    /* 카드 컨테이너 */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05) !important;
        background: #FFFFFF !important;
        padding: 14px !important;
        margin-bottom: 14px !important;
    }

    /* 모바일 가로 슬라이더 */
    .carousel-container {
        display: flex;
        overflow-x: auto;
        scroll-snap-type: x mandatory;
        gap: 8px;
        padding-bottom: 4px;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
    }
    .carousel-container::-webkit-scrollbar {
        display: none;
    }
    .carousel-img {
        flex: 0 0 78%;
        max-width: 250px;
        aspect-ratio: 1 / 1;
        object-fit: cover;
        border-radius: 12px;
        scroll-snap-align: start;
        box-shadow: 0 3px 8px rgba(0, 0, 0, 0.08);
    }

    /* 태그 뱃지 */
    .tag-container {
        margin: 6px 0 10px 0;
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
    }
    .tag-badge {
        display: inline-block;
        background: #EFF6FF;
        color: #1D4ED8;
        font-size: 11px;
        font-weight: 600;
        padding: 4px 9px;
        border-radius: 6px;
        border: 1px solid #BFDBFE;
    }
    .tag-badge-sub {
        background: #FFF1F2;
        color: #E11D48;
        border-color: #FECDD3;
    }

    /* 외부 링크 버튼 그리드 */
    .link-btn-grid {
        display: flex;
        gap: 6px;
        margin-bottom: 8px;
    }
    .map-btn, .insta-btn {
        flex: 1;
        display: flex !important;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: 700;
        height: 40px;
        border-radius: 10px;
        text-decoration: none !important;
        color: #FFFFFF !important;
    }
    .map-btn {
        background-color: #03C75A;
        box-shadow: 0 3px 8px rgba(3, 199, 90, 0.2);
    }
    .insta-btn {
        background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
        box-shadow: 0 3px 8px rgba(220, 39, 67, 0.2);
    }

    /* 모바일 버튼 최적화 */
    div[data-testid="stButton"] button {
        width: 100% !important;
        min-height: 40px !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 13px !important;
    }

    .plan-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 16px;
        margin-top: 12px;
        color: #1E293B;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 4. API 인증 설정
# -------------------------------------------------------------
client_id = st.secrets.get("NAVER_CLIENT_ID", "")
client_secret = st.secrets.get("NAVER_CLIENT_SECRET", "")

if not client_id or not client_secret:
    with st.sidebar:
        st.subheader("⚙️ API 인증 설정")
        client_id = st.text_input("Naver Client ID", type="password")
        client_secret = st.text_input("Naver Client Secret", type="password")

# -------------------------------------------------------------
# 5. 헬퍼 함수 정의
# -------------------------------------------------------------
def clean_html(text):
    return re.sub(r'<[^>]+>', '', text)

DEFAULT_IMAGES = {
    "🍽️ 맛집": [
        "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=1000&q=85",
        "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=1000&q=85"
    ],
    "☕ 카페": [
        "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=1000&q=85",
        "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=1000&q=85"
    ],
    "🏞️ 관광지": [
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1000&q=85",
        "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=1000&q=85"
    ],
    "🌙 야경": [
        "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=1000&q=85",
        "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=1000&q=85"
    ]
}

def generate_tags(raw_category, address, title, location_name=""):
    tags = []
    addr_match = re.search(r'([가-힣]+(?:읍|면|동|리|구|시))', address)
    if addr_match:
        loc_tag = addr_match.group(1).replace('특별자치도', '').replace('광역시', '').replace('특별시', '').replace('시', '').replace('구', '').replace('읍', '').replace('면', '')
        if len(loc_tag) >= 2:
            tags.append(f"#{loc_tag}핫플")

    cat_parts = [p.strip() for p in raw_category.split('>') if p.strip()]
    for part in cat_parts:
        if part not in ["음식점", "카페,디저트", "여행,명소", "관광,명소"]:
            tags.append(f"#{part}")

    clean_loc = re.sub(r'(특별자치도|광역시|특별시|자치도|시|도)$', '', location_name.strip())
    if not clean_loc:
        clean_loc = location_name.strip()

    if "카페" in raw_category or "디저트" in raw_category:
        tags.extend(["#오션뷰", "#감성카페"])
    elif "음식점" in raw_category:
        tags.extend([f"#{clean_loc}맛집" if clean_loc else "#지역맛집", "#식도락"])
    else:
        tags.extend(["#인생샷", f"#{clean_loc}여행" if clean_loc else "#국내여행"])

    unique_tags = list(dict.fromkeys(tags))[:4]
    
    html = '<div class="tag-container">'
    for i, t in enumerate(unique_tags):
        cls = "tag-badge-sub" if i % 2 == 1 else ""
        html += f'<span class="tag-badge {cls}">{t}</span>'
    html += '</div>'
    return html

def generate_carousel_html(img_urls):
    html = '<div class="carousel-container">'
    for url in img_urls:
        html += f'<img src="{url}" class="carousel-img" alt="place_img" loading="lazy"/>'
    html += '</div>'
    return html

# -------------------------------------------------------------
# 6. API 캐싱 처리 함수
# -------------------------------------------------------------
@st.cache_data(ttl=3600)
def fetch_naver_search(query, c_id, c_secret):
    url = "https://naverapihub.apigw.ntruss.com/search/v1/local"
    headers = {"X-NCP-APIGW-API-KEY-ID": c_id, "X-NCP-APIGW-API-KEY": c_secret}
    params = {"query": query, "display": 10, "start": 1, "sort": "comment"}
    
    try:
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            items = res.json().get("items", [])
            seen_titles = set()
            unique_items = []
            for item in items:
                clean_title = clean_html(item.get("title", ""))
                if clean_title not in seen_titles:
                    seen_titles.add(clean_title)
                    unique_items.append(item)
            return unique_items
    except Exception:
        pass
    return []

@st.cache_data(ttl=3600)
def get_place_images(location_name, place_title, category_key, c_id, c_secret, display_count=6):
    url = "https://naverapihub.apigw.ntruss.com/search/v1/image"
    headers = {"X-NCP-APIGW-API-KEY-ID": c_id, "X-NCP-APIGW-API-KEY": c_secret}
    params = {"query": f"{location_name} {place_title}", "display": display_count * 2, "sort": "sim"}
    img_list = []
    try:
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            items = res.json().get("items", [])
            for item in items:
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
# 7. 동선 정렬 함수 (날짜별 그룹화 지원)
# -------------------------------------------------------------
def generate_smart_schedule(itinerary_list):
    grouped_by_date = {}
    for item in itinerary_list:
        d_str = str(item.get("date", "날짜 미정"))
        if d_str not in grouped_by_date:
            grouped_by_date[d_str] = []
        grouped_by_date[d_str].append(item)

    plan_md = "### 🗺️ 날짜별 추천 최적 여행 동선\n\n"

    for visit_date in sorted(grouped_by_date.keys()):
        plan_md += f"#### 📅 {visit_date}\n"
        day_items = grouped_by_date[visit_date]
        
        meals, cafes, spots, nights, others = [], [], [], [], []
        for item in day_items:
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
        if spots: schedule.append(("10:00 - 12:00 [오전 관광]", spots.pop(0)))
        elif cafes: schedule.append(("10:30 - 12:00 [오전 티타임]", cafes.pop(0)))

        if meals: schedule.append(("12:30 - 14:00 [점심 식사]", meals.pop(0)))
        if cafes: schedule.append(("14:30 - 16:00 [디저트 & 카페]", cafes.pop(0)))
        if spots: schedule.append(("16:00 - 18:00 [오후 관광]", spots.pop(0)))
        if meals: schedule.append(("18:30 - 20:00 [저녁 식사]", meals.pop(0)))
        if nights: schedule.append(("20:30 - 21:30 [야경 코스]", nights.pop(0)))

        remaining = spots + meals + cafes + nights + others
        for rem in remaining:
            schedule.append(("자유 방문 추천 장소", rem))

        for time_slot, place in schedule:
            plan_md += f"**{time_slot}**  \n"
            plan_md += f"└ 📍 **{place['title']}** (`{place['category']}`)  \n"
            plan_md += f"   *주소: {place['address']}*  \n\n"

    return plan_md

# -------------------------------------------------------------
# 8. 메인 UI
# -------------------------------------------------------------
st.markdown("""
    <div class="hero-container">
        <div class="hero-title">✨ TRIP LOG</div>
        <div class="hero-subtitle">인스타 감성 핫플 & 스마트 여행 플래너</div>
    </div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🧭 감성 핫플 탐색", f"🗓️ 나의 코스 ({len(st.session_state.itinerary)})"])

with tab1:
    location = st.text_input("📍 떠나실 목적지", value="", placeholder="예: 제주도, 강릉, 속초, 부산, 여수")

    sub_area = "전체"
    if location and "제주" in location:
        sub_area = st.selectbox("🏝️ 제주 세부 지역", ["전체", "애월/한림", "서귀포/중문", "성산/구좌", "제주시/조천"])

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

    if location.strip():
        if not client_id or not client_secret:
            st.info("💡 사이드바 또는 Streamlit Secrets에 Naver API Key를 설정해 주세요.")
        else:
            clean_category = category.split()[-1]
            
            search_location = location
            if "제주" in location and sub_area != "전체":
                search_location = f"제주 {sub_area.split('/')[0]}"
            
            query = f"{search_location} {subcategory}" if subcategory != "전체" else f"{search_location} {clean_category}"
            
            items = fetch_naver_search(query, client_id, client_secret)
            
            if items:
                st.write("")
                st.markdown(f"#### 📸 **{search_location}** 인기 {query.replace(search_location, '').strip()} TOP {len(items)}")
                
                for idx, item in enumerate(items, 1):
                    title = clean_html(item.get("title", ""))
                    address = item.get("roadAddress") or item.get("address", "")
                    raw_cat = item.get("category", "")
                    
                    img_urls = get_place_images(search_location, title, category, client_id, client_secret, display_count=6)
                    
                    map_query = urllib.parse.quote(f"{search_location} {title}")
                    map_url = f"https://map.naver.com/v5/search/{map_query}"
                    
                    insta_query = urllib.parse.quote(f"{search_location}{title}".replace(" ", ""))
                    insta_url = f"https://www.instagram.com/explore/tags/{insta_query}/"
                    
                    with st.container(border=True):
                        st.markdown(generate_carousel_html(img_urls), unsafe_allow_html=True)
                        
                        st.write("")
                        st.markdown(f"#### **{idx}. {title}**")
                        st.markdown(generate_tags(raw_cat, address, title, location_name=search_location), unsafe_allow_html=True)
                        st.caption(f"📍 {address}")
                        
                        st.markdown(f'''
                            <div class="link-btn-grid">
                                <a href="{map_url}" target="_blank" class="map-btn">🟢 네이버 지도 ↗</a>
                                <a href="{insta_url}" target="_blank" class="insta-btn">📸 인스타그램 ↗</a>
                            </div>
                        ''', unsafe_allow_html=True)
                        
                        with st.popover("➕ 일정 담기", use_container_width=True):
                            selected_date = st.date_input("방문 날짜 선택", value=date.today(), key=f"date_{idx}_{title}")
                            if st.button("확인 및 일정 추가", key=f"add_btn_{idx}_{title}"):
                                is_duplicate = any(p['title'] == title and p['date'] == selected_date for p in st.session_state.itinerary)
                                if not is_duplicate:
                                    db_id = None
                                    try:
                                        res = supabase.table("my_courses").insert({
                                            "title": title, 
                                            "category": raw_cat, 
                                            "address": address,
                                            "visit_date": str(selected_date)
                                        }).execute()
                                        if res.data:
                                            db_id = res.data[0].get("id")
                                    except Exception as e:
                                        pass
                                    
                                    place_info = {
                                        "id": db_id,
                                        "title": title, 
                                        "address": address, 
                                        "category": raw_cat,
                                        "date": selected_date
                                    }
                                    st.session_state.itinerary.append(place_info)
                                    st.toast(f"✅ [{selected_date}] '{title}' 일정 추가!")
                                    st.rerun()
                                else:
                                    st.toast("⚠️ 이미 해당 날짜에 담긴 장소입니다.")
            else:
                st.warning("검색 결과가 없습니다.")
    else:
        st.info("💡 위 입력창에 목적지(예: 강릉, 부산 등)를 입력해 주세요.")

# -------------------------------------------------------------
# TAB 2: 담은 일정 코스
# -------------------------------------------------------------
with tab2:
    if st.session_state.itinerary:
        st.subheader("📋 선택한 장소 목록")
        
        # 날짜별 오름차순 정렬
        sorted_itinerary = sorted(st.session_state.itinerary, key=lambda x: x['date'])
        
        itinerary_text = ""
        current_date = None
        
        for i, place in enumerate(sorted_itinerary, 1):
            if current_date != place['date']:
                current_date = place['date']
                st.markdown(f"#### 📅 {current_date}")
                itinerary_text += f"\n[📅 {current_date}]\n"
                
            col_item, col_edit, col_del = st.columns([3, 1.2, 0.8])
            with col_item:
                st.write(f"**{place['title']}** (`{place['category']}`)")
                st.caption(f"📍 {place['address']}")
            
            # 📅 날짜 수정 Popover
            with col_edit:
                with st.popover("📅 날짜 변경", use_container_width=True):
                    new_date = st.date_input("새 방문 날짜", value=place['date'], key=f"edit_date_{i}_{place['title']}")
                    if st.button("변경 저장", key=f"save_date_{i}_{place['title']}"):
                        place['date'] = new_date
                        if place.get('id'):
                            try:
                                supabase.table("my_courses").update({"visit_date": str(new_date)}).eq("id", place['id']).execute()
                            except Exception as e:
                                pass
                        st.toast(f"📅 날짜 변경 완료: {new_date}")
                        st.rerun()

            with col_del:
                if st.button("삭제", key=f"del_state_{i}_{place['title']}"):
                    if place.get('id'):
                        try:
                            supabase.table("my_courses").delete().eq("id", place['id']).execute()
                        except Exception as e:
                            pass
                    st.session_state.itinerary.remove(place)
                    st.rerun()
                    
            itinerary_text += f"- {place['title']} ({place['category']}) - {place['address']}\n"
        
        st.write("")
        if st.button("🗑️ 일정 전체 비우기"):
            st.session_state.itinerary = []
            st.session_state.schedule_plan = ""
            try:
                supabase.table("my_courses").delete().neq("id", 0).execute()
            except Exception as e:
                pass
            st.rerun()

        st.write("---")
        st.subheader("⚡ 1초 자동 동선 정렬")
        st.caption("장소 성격과 날짜에 맞춰 가장 효율적인 시간대별 동선을 짜드립니다.")
        
        if st.button("🚀 시간대별 자동 일정표 생성하기"):
            st.session_state.schedule_plan = generate_smart_schedule(st.session_state.itinerary)
            st.success("🎉 최적 동선 일정표 생성 완료!")

        if st.session_state.schedule_plan:
            st.markdown('<div class="plan-box">', unsafe_allow_html=True)
            st.markdown(st.session_state.schedule_plan)
            st.markdown('</div>', unsafe_allow_html=True)

        st.write("---")
        st.text_area("📋 일정 텍스트 복사 (카톡/메모장 공유용)", value=itinerary_text.strip(), height=150)

    else:
        st.info("💡 **'🧭 감성 핫플 탐색'** 탭에서 마음에 드는 장소의 **'➕ 일정 담기'** 버튼을 눌러 나만의 코스를 담아보세요!")
