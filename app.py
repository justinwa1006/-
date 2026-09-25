import streamlit as st
import requests
import re
import urllib.parse

# 1. 페이지 레이아웃 설정 (시스템 다크/라이트 테마 자동 반영)
st.set_page_config(
    page_title="TRIP LOG · 여행 가이드",
    page_icon="✈️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. 다크 모드 / 라이트 모드 자동 반응형 커스텀 CSS
st.markdown("""
    <style>
    /* 라이트 모드 기본 스타일 */
    :root {
        --card-bg: #FFFFFF;
        --card-border: #E2E8F0;
        --text-primary: #0F172A;
        --text-secondary: #64748B;
        --text-address: #334155;
        --badge-bg: #EFF6FF;
        --badge-text: #1D4ED8;
    }

    /* 다크 모드 스타일 */
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

    /* 상단 배너 히어로 헤더 */
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

    /* 카드 스타일 */
    .place-card {
        background-color: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        transition: background-color 0.3s ease, border-color 0.3s ease;
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
        gap: 4px;
        background-color: #03C75A;
        color: #FFFFFF !important;
        font-size: 12px;
        font-weight: 600;
        padding: 8px 14px;
        border-radius: 6px;
        text-decoration: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 사이드바 설정
with st.sidebar:
    st.subheader("⚙️ API 인증 설정")
    client_id = st.text_input("Naver Client ID", type="password")
    client_secret = st.text_input("Naver Client Secret", type="password")
    st.caption("NAVER API HUB에서 발급받은 인증키를 입력해주세요.")

# 4. 상단 히어로 헤더 (TOP 10으로 수정)
st.markdown("""
    <div class="hero-container">
        <div class="hero-title">✈️ TRIP LOG</div>
        <div class="hero-subtitle">네이버 실시간 지역 데이터 기반 TOP 10 가이드</div>
    </div>
""", unsafe_allow_html=True)

# 5. 사용자 입력 폼 (기본값 제거 / 빈칸 설정)
location = st.text_input("📍 떠나실 목적지를 입력해 보세요", value="", placeholder="예: 제주도, 강릉, 속초, 부산")
category = st.radio("카테고리 선택", ["🍽️ 맛집", "☕ 카페", "🏞️ 관광지", "🌙 야경"], horizontal=True)

def clean_html(text):
    return re.sub(r'<[^>]+>', '', text)

# 6. 결과 출력
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
        query = f"{location} {clean_category}"
        
        # display를 10으로 설정하여 최대 10개까지 출력
        params = {
            "query": query,
            "display": 10,
            "start": 1,
            "sort": "comment"
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                
                if items:
                    st.write("")
                    st.markdown(f"#### 🔍 **{location}** 인기 {clean_category} TOP {len(items)}")
                    
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
                else:
                    st.warning("검색 결과가 없습니다.")
            else:
                st.error(f"API 오류 발생 ({response.status_code}): 키 정보를 다시 확인해주세요.")
        except Exception as e:
            st.error(f"요청 중 오류가 발생했습니다: {e}")
