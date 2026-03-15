import streamlit as st
import requests
import json
from datetime import datetime

# 1. 노션 설정
NOTION_TOKEN = st.secrets.get("NOTION_TOKEN", "")
DATABASE_ID = st.secrets.get("DATABASE_ID", "")

st.set_page_config(page_title="영업 상담 일지", page_icon="📝", layout="centered")

# 2. 담당자 자동 인식 및 선택 로직
query_params = st.query_params
user_param = query_params.get("user", None)

st.title("📝 영업 상담 일지 등록")

if user_param:
    current_agent = user_param
    st.success(f"✅ 접속 담당자: **{current_agent}**님 (자동 인식됨)")
else:
    current_agent = st.selectbox(
        "작성자를 선택해주세요", 
        ["다니엘", "이정현", "팀원A", "팀원B", "팀원C"],
        index=None,
        placeholder="담당자 선택 필수"
    )

st.divider()

# 3. 입력 폼 구성
with st.form("consulting_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        company = st.text_input("업체명 *")
        contact = st.text_input("연락처")
        
    with col2:
        # multiselect로 변경하여 중복 선택 가능하게 수정
        categories = st.multiselect("상담 항목 (중복 선택 가능) *", 
                                   ["수전합리화", "태양광", "법인", "광고", "백렌탈"])
        clova_link = st.text_input("클로바 노트 링크")

    meeting_notes = st.text_area("미팅 내용", height=150)
    other_notes = st.text_area("기타 특이사항", height=100)
    
    submit_button = st.form_submit_button("노션으로 전송하기")

# 4. 노션 전송 로직
if submit_button:
    if not company:
        st.error("업체명은 필수 입력 사항입니다!")
    elif not categories:
        st.error("상담 항목을 최소 하나 이상 선택해주세요!")
    elif not current_agent:
        st.error("작성자를 선택해주세요!")
    else:
        today = datetime.now().strftime("%Y-%m-%d")
        
        headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

        # 다중 선택(multi_select) 형식에 맞게 데이터 변환
        multi_select_list = [{"name": cat} for cat in categories]

        payload = {
            "parent": {"database_id": DATABASE_ID},
            "properties": {
                "업체명": {"title": [{"text": {"content": company}}]},
                "연락처": {"rich_text": [{"text": {"content": contact}}]},
                "상담항목": {"multi_select": multi_select_list}, # multi_select로 변경
                "미팅내용": {"rich_text": [{"text": {"content": meeting_notes}}]},
                "기타 특이사항": {"rich_text": [{"text": {"content": other_notes}}]},
                "상담자": {"select": {"name": current_agent}},
                "클로바링크": {"url": clova_link if clova_link else None},
                "작성일": {"date": {"start": today}}
            }
        }

        try:
            response = requests.post("https://api.notion.com/v1/pages", 
                                     headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                st.balloons()
                st.success(f"✅ [{company}] 상담 기록이 성공적으로 등록되었습니다!")
            else:
                st.error(f"❌ 전송 실패: {response.text}")
        except Exception as e:
            st.error(f"❌ 오류 발생: {e}")

st.caption("시스템 문의: 이정현 (Sales Pro Product Developer)")
