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

# 2. 세션 스테이트 초기화 (일정 담기 기능용)
if "itinerary" not in st.session_state:
    st.session_state.itinerary = []

# 3. 커스텀 CSS (반응형 다크/라이트 테마 + 버튼 스타일)
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
        }
    }

    .hero-container {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 24px 20px;
        border-radius: 16px;
        color: #FFFFFF !important;
        margin-bottom: 24px;
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
        <div class="hero-subtitle">네이버 실시간 데이터 기반 맞춤 여행 가이드</div>
    </div>
""", unsafe_allow_html=True)

# 6. 사용자 입력 & 세부 분류 폼
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

def clean_html(text):
    return re.sub(r'<[^>]+>', '', text)

# 7. 검색 실행
if location:
    if not client_id or not client_secret:
        st.info("💡 왼쪽 사이드바에 Naver API Client ID와 Secret을 입력해 주세요.")
    else:
        url = "https://naverapihub.apigw.ntruss.com/search/v1/local"
        headers = {
            "X-NCP-APIGW-API-KEY-ID": client_id,
            "X-NCP-APIGW-API-KEY": client_secret
        }
        
        # 세부 카테고리가 지정된 경우 검색어 조합
        clean_category = category.split()[-1]
        if subcategory != "전체":
            query = f"{location} {subcategory}"
        else:
            query = f"{location} {clean_category}"
        
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
                    
                    # 장소 카드 출력
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
                    
                    # 일정 담기 버튼
                    place_info = {"title": title, "address": address, "category": cat}
                    if st.button(f"➕ '{title}' 일정에 담기", key=f"add_{idx}_{title}"):
                        if place_info not in st.session_state.itinerary:
                            st.session_state.itinerary.append(place_info)
                            st.toast(f"✅ '{title}' 장소가 일정표에 추가되었습니다!")
                        else:
                            st.toast(f"⚠️ 이미 일정에 담긴 장소입니다.")
            else:
                st.warning("검색 결과가 없습니다.")
        except Exception as e:
            st.error(f"요청 중 오류가 발생했습니다: {e}")

# 8. 담은 일정표 섹션
st.write("---")
st.subheader(f"🗓️ 나의 여행 일정표 ({len(st.session_state.itinerary)}개)")

if st.session_state.itinerary:
    itinerary_text = ""
    for i, place in enumerate(st.session_state.itinerary, 1):
        col_item, col_del = st.columns([5, 1])
        with col_item:
            st.write(f"**{i}. {place['title']}** ({place['category']})")
            st.caption(f"📍 {place['address']}")
        with col_del:
            if st.button("삭제", key=f"del_{i}"):
                st.session_state.itinerary.pop(i - 1)
                st.rerun()
        itinerary_text += f"{i}. {place['title']} - {place['address']}\n"
    
    st.write("")
    if st.button("🗑️ 일정 전체 비우기"):
        st.session_state.itinerary = []
        st.rerun()
        
    st.text_area("📋 일정 목록 텍스트 (복사해서 카톡/메모장에 공유하세요)", value=itinerary_text, height=120)
else:
    st.info("검색 목록에서 마음에 드는 장소의 '➕ 일정에 담기' 버튼을 눌러 나만의 여행 코스를 짜보세요!")
