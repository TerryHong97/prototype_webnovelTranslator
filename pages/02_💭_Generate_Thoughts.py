### Import ###
import streamlit as st
import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

### Page Configuration ###
st.set_page_config(
    page_title="Generate Thoughts",
    page_icon="💭",
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
def create_prompt_for_glossary():
    # 현재 파일의 디렉토리 경로
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # prompts 폴더 내의 파일 경로
    file_path_input1 = os.path.join(current_dir, '..', 'prompts', 'glossaryFSL_input1.txt')
    file_path_output1 = os.path.join(current_dir, '..', 'prompts', 'glossaryFSL_output1.txt')
    file_path_SYSTEM = os.path.join(current_dir, '..', 'prompts', 'glossary_SYSTEM.txt')

    # read_message 함수를 사용하여 파일 읽기
    FSL_input1 = read_message(file_path_input1)
    FSL_output1 = read_message(file_path_output1)
    SYSTEM = read_message(file_path_SYSTEM)

     # 예시 설정
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

@st.cache_data
def create_prompt_for_sound_effect():
    # 현재 파일의 디렉토리 경로
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # prompts 폴더 내의 파일 경로
    file_path_input1 = os.path.join(current_dir, '..', 'prompts', 'sound-effectsFSL_input1.txt')
    file_path_output1 = os.path.join(current_dir, '..', 'prompts', 'sound-effectsFSL_output1.txt')
    file_path_SYSTEM = os.path.join(current_dir, '..', 'prompts', 'sound-effects_SYSTEM.txt')

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

@st.cache_data
def create_prompt_for_line_context():
    # 현재 파일의 디렉토리 경로
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # prompts 폴더 내의 파일 경로
    file_path_input1 = os.path.join(current_dir, '..', 'prompts', 'line_contextFSL_input1.txt')
    file_path_output1 = os.path.join(current_dir, '..', 'prompts', 'line_contextFSL_output1.txt')
    file_path_input2 = os.path.join(current_dir, '..', 'prompts', 'line_contextFSL_input2.txt')
    file_path_output2 = os.path.join(current_dir, '..', 'prompts', 'line_contextFSL_output2.txt')
    file_path_SYSTEM = os.path.join(current_dir, '..', 'prompts', 'line_context_SYSTEM.txt')

    # read_message 함수를 사용하여 파일 읽기
    FSL_input1 = read_message(file_path_input1)
    FSL_output1 = read_message(file_path_output1)
    FSL_input2 = read_message(file_path_input2)
    FSL_output2 = read_message(file_path_output2)
    SYSTEM = read_message(file_path_SYSTEM)

    # 예시 설정 (Few-shot Learning)
    examples = [
        {
            "input": FSL_input1,
            "output": FSL_output1
        },
        {
            "input": FSL_input2,
            "output": FSL_output2
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
def glossary_step1_generate_draft(input_txt):

    final_prompt = create_prompt_for_glossary()
    model = generate_model(st.session_state["OPENAI_API_KEY"])
    parser = JsonOutputParser()
    
    chain = final_prompt | model | parser

    glossary_draft = chain.invoke({"input_txt": input_txt})
    
    return glossary_draft

def glossary_step2_update_draft(glossary_draft, previous_glossary):
    # 이전 용어집을 딕셔너리로 변환하여 Korean 용어를 키로, English와 status를 값으로 저장
    previous_dict = {entry["Korean"]: {"English": entry["English"], "status": "previous"} for entry in previous_glossary}

    # glossary_draft를 업데이트
    for entry in glossary_draft:
        korean_term = entry["Korean"]
        if korean_term in previous_dict:
            entry["English"] = previous_dict[korean_term]["English"]
            entry["status"] = "previous"

    return glossary_draft

def add_status_to_json(json_data):
    for item in json_data:
        item["status"] = "new"
    return json_data

@st.cache_data(show_spinner=True)
def sound_effect_generate_info(input_txt):

    final_prompt = create_prompt_for_sound_effect()
    model = generate_model(st.session_state["OPENAI_API_KEY"])
    parser = JsonOutputParser()

    chain = final_prompt | model | parser

    sound_effect_info = chain.invoke({"input_txt": input_txt})

    return sound_effect_info

@st.cache_data(show_spinner=True)
def line_context_generate_info(input_txt):
    final_prompt = create_prompt_for_line_context()
    model = generate_model(st.session_state["OPENAI_API_KEY"])
    parser = JsonOutputParser()

    chain = final_prompt | model | parser

    line_context_info = chain.invoke({"input_txt": input_txt})

    return line_context_info


### Painting UI with Streamlit ###

st.title("번역 정보 생성")

col_left, col_right = st.columns(2)

with col_left:
    st.header("웹소설 원문")
    with st.container(height=675):
        st.write(st.session_state["Original_Text"])
    

with col_right:
    st.header("정보 유형")
    tab_glossary, tab_sound_effect, tab_line_context = st.tabs(["용어집", "효과음", "대사 정보"])

    with tab_glossary:
        button_glossary = st.button("용어집 생성")
        if button_glossary and (st.session_state["Info_1_Glossary"] == None):
            st.session_state["Info_1_Glossary"] = add_status_to_json(glossary_step1_generate_draft(st.session_state["Original_Text"]))
            if st.session_state["Previous_Glossary"] != []:
                glossary_step2_update_draft(st.session_state["Info_1_Glossary"], st.session_state["Previous_Glossary"])
        
        if button_glossary and st.session_state["Info_1_Glossary"] != None:
            editing_glossary_str = json.dumps(st.session_state["Info_1_Glossary"], ensure_ascii=False, indent=4)
        elif st.session_state["Info_1_Glossary"] != None:
            editing_glossary_str = json.dumps(st.session_state["Info_1_Glossary"], ensure_ascii=False, indent=4)
        else:
            editing_glossary_str = ""
        
        with st.form("edit_glossary"):
            glossary_edited = st.text_area(label="용어집 확인 및 수정", value=editing_glossary_str, height=443)
            submitted = st.form_submit_button("저장하기")
            if submitted:
                st.session_state["Info_1_Glossary"] = json.loads(glossary_edited)
                st.success("용어집 저장 완료!")
    
    with tab_sound_effect:
        button_sound_effect = st.button("효과음 정보 생성")
        if button_sound_effect and (st.session_state["Info_2_Sound_Effect"] == None):
            st.session_state["Info_2_Sound_Effect"] = sound_effect_generate_info(st.session_state["Original_Text"])
    
        if button_sound_effect and st.session_state["Info_2_Sound_Effect"] != None:
            editing_sound_effect_str = json.dumps(st.session_state["Info_2_Sound_Effect"], ensure_ascii=False, indent=4)
        elif st.session_state["Info_2_Sound_Effect"] != None:
            editing_sound_effect_str = json.dumps(st.session_state["Info_2_Sound_Effect"], ensure_ascii=False, indent=4)
        else:
            editing_sound_effect_str = ""

        with st.form("edit_sound_effect"):
            sound_effect_edited = st.text_area(label="효과음 정보 확인 및 수정", value=editing_sound_effect_str, height=443)
            submitted = st.form_submit_button("저장하기")
            if submitted:
                st.session_state["Info_2_Sound_Effect"] = json.loads(sound_effect_edited)
                st.success("효과음 정보 저장 완료!")

    with tab_line_context:
        button_line_context = st.button("대사 맥락정보 생성")
        if button_line_context and (st.session_state["Info_3_Line_Context"] == None):
            st.session_state["Info_3_Line_Context"] = line_context_generate_info(st.session_state["Original_Text"])
    
        if button_line_context and st.session_state["Info_3_Line_Context"] != None:
            editing_line_context_str = json.dumps(st.session_state["Info_3_Line_Context"], ensure_ascii=False, indent=4)
        elif st.session_state["Info_3_Line_Context"] != None:
            editing_line_context_str = json.dumps(st.session_state["Info_3_Line_Context"], ensure_ascii=False, indent=4)
        else:
            editing_line_context_str = ""

        with st.form("edit_line_context"):
            line_context_edited = st.text_area(label="대사 맥락정보 확인 및 수정", value=editing_line_context_str, height=443)
            submitted = st.form_submit_button("저장하기")
            if submitted:
                st.session_state["Info_3_Line_Context"] = json.loads(line_context_edited)
                st.success("대사 맥락정보 저장 완료!")



notice_glossary, notice_sound_effect, notice_line_context = st.columns(3)

with notice_glossary:
    if st.session_state["Info_1_Glossary"] == None:
        st.warning("용어집 생성되지 않음", icon="🚨")
    else:
        st.success("용어집 생성 완료", icon="✅")
        st.json(st.session_state["Info_1_Glossary"], expanded=True)

with notice_sound_effect:
    if st.session_state["Info_2_Sound_Effect"] == None:
        st.warning("효과음 정보 생성되지 않음", icon="🚨")
    else:
        st.success("효과음 정보 생성 완료", icon="✅")
        st.json(st.session_state["Info_2_Sound_Effect"], expanded=True)

with notice_line_context:
    if st.session_state["Info_3_Line_Context"] == None:
        st.warning("대사 맥락정보 생성되지 않음", icon="🚨")
    else:
        st.success("대사 맥락정보 생성 완료", icon="✅")
        st.json(st.session_state["Info_3_Line_Context"], expanded=True)