import streamlit as st
import requests
import re
import urllib.parse

# 1. 페이지 레이아웃 및 제목 설정
st.set_page_config(
    page_title="TRIP LOG · 여행 가이드",
    page_icon="✈️",
    layout="centered"
)

# 2. 전문 모바일 UI 커스텀 CSS 스타일링
st.markdown("""
    <style>
    /* 배경색 및 기본 폰트 */
    .stApp {
        background-color: #F8FAFC;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    
    /* 사이드바 스타일링 */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    
    /* 상단 배너 히어로 헤더 */
    .hero-container {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 24px 20px;
        border-radius: 16px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 15px -3px rgba(30, 58, 138, 0.15);
    }
    .hero-title {
        font-size: 22px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
    }
    .hero-subtitle {
        font-size: 13px;
        color: #E0E7FF;
        margin-top: 6px;
    }
    
    /* 추천 장소 카드 스타일 */
    .place-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .place-badge {
        display: inline-block;
        background-color: #EFF6FF;
        color: #1D4ED8;
        font-size: 11px;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    .place-title {
        font-size: 16px;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 4px;
    }
    .place-category {
        font-size: 12px;
        color: #64748B;
        margin-bottom: 8px;
    }
    .place-address {
        font-size: 13px;
        color: #334155;
        margin-bottom: 12px;
    }
    .map-btn {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background-color: #03C75A;
        color: white !important;
        font-size: 12px;
        font-weight: 600;
        padding: 6px 12px;
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

# 4. 상단 히어로 헤더
st.markdown("""
    <div class="hero-container">
        <div class="hero-title">✈️ TRIP LOG</div>
        <div class="hero-subtitle">네이버 실시간 지역 데이터 기반 TOP 5 가이드</div>
    </div>
""", unsafe_allow_html=True)

# 5. 사용자 입력 폼
location = st.text_input("📍 떠나실 목적지를 입력해 보세요", placeholder="예: 강릉, 속초, 부산")
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
        
        params = {
            "query": query,
            "display": 5,
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
                    st.markdown(f"#### 🔍 **{location}** 인기 {clean_category}")
                    
                    for idx, item in enumerate(items, 1):
                        title = clean_html(item.get("title", ""))
                        address = item.get("roadAddress") or item.get("address", "")
                        cat = item.get("category", "")
                        
                        map_query = urllib.parse.quote(f"{location} {title}")
                        map_url = f"https://map.naver.com/v5/search/{map_query}"
                        
                        # 카드형 HTML 레더링
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
