### Import ###
import streamlit as st
import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

### Page Configuration ###
st.set_page_config(
    page_title="Final Translation",
    page_icon="🔄️",
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

### Functions ###
@st.cache_data
def read_message(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            message = file.read()
            return message
    except FileNotFoundError:
        return "The file was not found."
    except Exception as e:
        return f"An error occurred: {e}"

@st.cache_resource
def generate_model(api_key):
    return ChatOpenAI(model="gpt-4o", api_key=api_key)

@st.cache_data
def create_input_text_for_final_translation(glossary, tag_prompted_text):
    # JSON -> 문자열
    glossary_str = json.dumps(glossary, ensure_ascii=False, indent=4)

    # 구분자 만들기
    flag_glossary = "###glossary: must be reflected for consistent translation###\n"
    flag_tag_prompted_txt = "###Korean webnovel with tag prompting: need to be translated###\n"

    # 인풋 텍스트 생성
    input_txt = flag_glossary + glossary_str + "\n\n" + flag_tag_prompted_txt + tag_prompted_text

    return input_txt

@st.cache_data
def create_prompt_for_final_translation():

    # 현재 파일의 디렉토리 경로
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # prompts 폴더 내의 파일 경로
    file_path_input1 = os.path.join(current_dir, '..', 'prompts', 'final_translationFSL_input1.txt')
    file_path_output1 = os.path.join(current_dir, '..', 'prompts', 'final_translationFSL_output1.txt')
    file_path_SYSTEM = os.path.join(current_dir, '..', 'prompts', 'final_translation_SYSTEM.txt')

    # read_message 함수를 사용하여 파일 읽기
    FSL_input1 = read_message(file_path_input1)
    FSL_output1 = read_message(file_path_output1)
    SYSTEM = read_message(file_path_SYSTEM)

    # 예시 설정 (Few-shot Learning)
    examples = [
        {
            "input": FSL_input1,
            "output": FSL_output1
        }
    ]

    # 프롬프트 구성
    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{input}"),
            ("ai", "{output}"),
        ]
    )
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=examples,
    )
    final_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM),
            few_shot_prompt,
            ("human", "{input_txt}"),
        ]
    )

    return final_prompt

@st.cache_data(show_spinner=True)
def final_translation(input_txt):

    final_prompt = create_prompt_for_final_translation()
    model = generate_model(st.session_state["OPENAI_API_KEY"])
    parser = StrOutputParser()

    chain = final_prompt | model | parser

    final_translate = chain.invoke({"input_txt": input_txt})

    return final_translate

### Painting UI with Streamlit ###

st.title("최종 번역")

col_left, col_right = st.columns(2)

with col_left:
    st.header("웹소설 원문")
    with st.container(height=675):
        st.write(st.session_state["Original_Text"])


with col_right:
    st.header("웹소설 번역문")
    button_final_translate = st.button("최종 번역 시작")
    if button_final_translate:
        st.session_state["Final_Translation"] = final_translation(st.session_state["Tag_Prompted_Text_with_glossary"])
    
    with st.container(height=600):
        st.write(st.session_state["Final_Translation"])