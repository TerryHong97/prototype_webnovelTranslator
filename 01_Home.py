### Import ###
import streamlit as st
import json
from io import StringIO


### Page Configuration ###
st.set_page_config(
    page_title="Home",
    page_icon="🏠",
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
if "Tag_Prompted_Text_with_glossary" not in st.session_state:
    st.session_state["Tag_Prompted_Text_with_glossary"] = None
if "Final_Translation" not in st.session_state:
    st.session_state["Final_Translation"] = None
if "Current_Glossary_for_Next_Chapter" not in st.session_state:
    st.session_state["Current_Glossary_for_Next_Chapter"] = None


### Painting UI with Streamlit ###
with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    if openai_api_key:
        st.session_state["OPENAI_API_KEY"] = openai_api_key
    
    if not st.session_state["OPENAI_API_KEY"].startswith("sk-"):
        st.warning("API 키가 필요합니다.", icon='⚠')
    else:
        st.success("API 키가 등록되었습니다.")

st.title("Home")

col_left, col_right = st.columns(2)

with col_left:
    uploaded_webnovel = st.file_uploader("웹소설 파일을 업로드 해주세요.")
    add_line_break = st.toggle("줄바꿈 추가", value=True)
    if uploaded_webnovel is not None:
        webnovel_text = uploaded_webnovel.read().decode('utf-8')
        if add_line_break:
            webnovel_text = webnovel_text.replace('\n', '\n\n')
        st.session_state["Original_Text"] = webnovel_text

    with st.container(height=550):
        st.write(st.session_state["Original_Text"])

with col_right:
    uploaded_glossary = st.file_uploader("반영할 용어집을 업로드 해주세요.")
    if uploaded_glossary is not None:
        stringio_glossary = StringIO(uploaded_glossary.getvalue().decode("utf-8"))
        glossary_json = json.loads(stringio_glossary.read())
        st.session_state["Previous_Glossary"] = glossary_json
    
    with st.container(height=550):
        st.write(st.session_state["Previous_Glossary"])

