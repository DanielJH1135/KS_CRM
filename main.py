import streamlit as st
import requests
import json
from datetime import datetime

# 1. 노션 설정
NOTION_TOKEN = st.secrets.get("NOTION_TOKEN", "")
DATABASE_ID = st.secrets.get("DATABASE_ID", "")

st.set_page_config(page_title="영업 상담 일지", page_icon="📝")

# 2. URL 파라미터로 담당자 인식
query_params = st.query_params
current_agent = query_params.get("user", "미지정")

st.title("📝 영업 상담 일지 등록")
st.caption(f"접속 담당자: {current_agent}")
st.divider()

# 3. 입력 폼 구성
with st.form("consulting_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        company = st.text_input("업체명 *")
        contact = st.text_input("연락처")
        
    with col2:
        # 노션 속성명에 맞춰 '상담항목' (띄어쓰기 제거)
        category = st.selectbox("상담 항목 *", 
                                ["수전합리화", "태양광", "법인", "광고", "백렌탈"])
        clova_link = st.text_input("클로바 노트 링크")

    meeting_notes = st.text_area("미팅 내용", height=150)
    other_notes = st.text_area("기타 특이사항", height=100)
    
    submit_button = st.form_submit_button("노션으로 전송하기")

# 4. 노션 전송 로직
if submit_button:
    if not company:
        st.error("업체명은 필수입니다!")
    else:
        # 오늘 날짜 가져오기 (YYYY-MM-DD 형식)
        today = datetime.now().strftime("%Y-%m-%d")
        
        headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

        # 노션 표의 실제 이름과 100% 일치하도록 매핑
        payload = {
            "parent": {"database_id": DATABASE_ID},
            "properties": {
                "업체명": {"title": [{"text": {"content": company}}]},
                "연락처": {"rich_text": [{"text": {"content": contact}}]},
                "상담항목": {"select": {"name": category}}, # 띄어쓰기 제거됨
                "미팅내용": {"rich_text": [{"text": {"content": meeting_notes}}]},
                "기타 특이사항": {"rich_text": [{"text": {"content": other_notes}}]}, # 띄어쓰기 추가됨
                "상담자": {"select": {"name": current_agent}},
                "클로바링크": {"url": clova_link if clova_link else None},
                "작성일": {"date": {"start": today}} # 새로 추가된 날짜 항목
            }
        }

        try:
            response = requests.post("https://api.notion.com/v1/pages", 
                                     headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                st.success(f"✅ {company} 상담 일지가 성공적으로 등록되었습니다!")
                st.balloons()
            else:
                st.error(f"❌ 전송 실패: {response.text}")
        except Exception as e:
            st.error(f"❌ 네트워크 오류: {e}")

st.info(f"💡 담당자 '{current_agent}'님으로 기록됩니다.")
