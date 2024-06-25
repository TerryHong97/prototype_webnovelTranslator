### Import ###
import streamlit as st
import json

### Page Configuration ###
st.set_page_config(
    page_title="Post Editing",
    page_icon="🛠️",
    layout="wide"
)

### Session State Initialize ###
if "OPENAI_API_KEY" not in st.session_state:
    st.session_state["OPENAI_API_KEY"] = ""
if "Original_Text" not in st.session_state:
    st.session_state["Original_Text"] = None
if "Previous_Glossary" not in st.session_state:
    st.session_state["Previous_Glossary"] = []
if "Info_1_Glossary" not in st.session_state:
    st.session_state["Info_1_Glossary"] = None
if "Info_2_Sound_Effect" not in st.session_state:
    st.session_state["Info_2_Sound_Effect"] = None
if "Info_3_Line_Context" not in st.session_state:
    st.session_state["Info_3_Line_Context"] = None
if "Tag_Prompted_Text" not in st.session_state:
    st.session_state["Tag_Prompted_Text"] = None
if "Final_Translation" not in st.session_state:
    st.session_state["Final_Translation"] = None
if "Current_Glossary_for_Next_Chapter" not in st.session_state:
    st.session_state["Current_Glossary_for_Next_Chapter"] = None


### Functions ###
@st.cache_data
def create_current_glossary(previous_glossary, glossary_of_this_chapter):
    # previous_glossary를 복제하여 temp 리스트 생성
    temp = previous_glossary.copy()
    
    # previous_glossary의 Korean 용어들을 set으로 저장
    previous_korean_terms = {entry["Korean"] for entry in previous_glossary}
    
    # glossary_of_this_chapter의 용어 중 previous_glossary에 없는 용어를 temp에 추가
    for entry in glossary_of_this_chapter:
        if entry["Korean"] not in previous_korean_terms:
            temp.append(entry)
    
    # temp의 모든 오브젝트의 "status"를 "previous"로 변경
    for entry in temp:
        entry["status"] = "previous"
    
    return temp


### Painting UI with Streamlit ###

st.title("교정 및 검수")

show_original_text, show_translated_text = st.columns(2)

with show_original_text:
    st.header("웹소설 원문")
    with st.container(height=620):
        st.write(st.session_state["Original_Text"])

with show_translated_text:
    st.header("웹소설 번역문")
    with st.form("edit_translated_text"):
        editing_translated_text = st.text_area(label="번역본 수정", 
                                               label_visibility="collapsed", 
                                               value=st.session_state["Final_Translation"],
                                               height=600)
        submitted = st.form_submit_button("수정하기")
        if submitted:
            st.session_state["Final_Translation"] = editing_translated_text
            st.success("번역본 수정 완료!")

st.header("번역본 및 용어집 다운로드")

col_1, col_2, col_3, col_4 = st.columns(4)

with col_1:
    if st.session_state["Current_Glossary_for_Next_Chapter"] == None:
        st.session_state["Current_Glossary_for_Next_Chapter"] = create_current_glossary(st.session_state["Previous_Glossary"],
                                                                                        st.session_state["Info_1_Glossary"])
    st.download_button(label="용어집 저장",
                       data=json.dumps(st.session_state["Current_Glossary_for_Next_Chapter"]),
                       file_name="current_glossary.json",
                       mime="application/json")

with col_2:
    st.download_button(label="효과음 정보 저장",
                       data=json.dumps(st.session_state["Info_2_Sound_Effect"]),
                       file_name="sound_effect.json",
                       mime="application/json")

with col_3:
    st.download_button(label="대사 맥락정보 저장",
                       data=json.dumps(st.session_state["Info_3_Line_Context"]),
                       file_name="line_context.json",
                       mime="application/json")

with col_4:
    st.download_button(label="번역본 저장", 
                       data=st.session_state["Final_Translation"],
                       file_name="translated_version.txt",
                       mime="text/plain",
                       type="primary")
