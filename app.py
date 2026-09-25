import streamlit as st
import requests
import re
import urllib.parse

# 페이지 기본 설정
st.set_page_config(page_title="TRIP LOG · TOP 10 가이드", page_icon="✈️", layout="wide")

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 설정")
    client_id = st.text_input("Naver Client ID", type="password")
    client_secret = st.text_input("Naver Client Secret", type="password")

# 메인 헤더
st.markdown("""
    <div style="background-color: #2B6CB0; padding: 20px; border-radius: 10px; color: white;">
        <h2 style="margin: 0;">✈️ TRIP LOG</h2>
        <p style="margin: 5px 0 0 0;">네이버 실시간 검색 기반 TOP 10 가이드</p>
    </div>
""", unsafe_allow_html=True)

st.write("")

# 검색어 입력 및 카테고리 선택
location = st.text_input("📍 어디로 떠나시나요?", value="제주도")
category = st.radio("카테고리", ["🍽️ 맛집", "☕ 카페", "🏞️ 관광지", "🌙 야경"], horizontal=True)

# HTML 태그 제거 함수
def clean_html(text):
    return re.sub(r'<[^>]+>', '', text)

# 검색 실행
if location:
    if not client_id or not client_secret:
        st.error("API 요청에 실패했습니다. Client ID와 Secret을 확인해 주세요.")
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
                    st.subheader(f"🔍 '{query}' 추천 장소 목록")
                    for idx, item in enumerate(items, 1):
                        title = clean_html(item.get("title", ""))
                        address = item.get("roadAddress") or item.get("address", "")
                        cat = item.get("category", "")
                        
                        # 네이버 지도 바로가기 URL 생성
                        map_query = urllib.parse.quote(f"{location} {title}")
                        map_url = f"https://map.naver.com/p/search/{map_query}"
                        
                        with st.expander(f"{idx}. {title}"):
                            st.write(f"**카테고리:** {cat}")
                            st.write(f"**주소:** {address}")
                            st.write(f"**📍 지도 위치:** [네이버 지도로 보기]({map_url})")
                else:
                    st.info("검색 결과가 없습니다.")
            else:
                st.error(f"API 오류 발생 (코드 {response.status_code}): Client ID/Secret 값을 다시 확인해주세요.")
        except Exception as e:
            st.error(f"요청 중 오류 발생: {e}")
