### Import ###
import streamlit as st
import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

### Page Configuration ###
st.set_page_config(
    page_title="Text Preprocessing",
    page_icon="🏷️",
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
def create_input_text_for_tag_prompting(original_txt, sound_effect, line_context):

    # JSON -> 문자열
    sound_effect_str = json.dumps(sound_effect, ensure_ascii=False, indent=4)
    line_context_str = json.dumps(line_context, ensure_ascii=False, indent=4)

    # 구분자 만들기
    flag_sound_effects = "###sound effects information given by JSON format###\n"
    flag_line_context = "###line context information given by JSON format###\n"
    flag_original_txt = "###original text of Korean webnovel : you should pinpoint the target and insert tags###\n"

    # 인풋 텍스트 생성
    input_txt = flag_sound_effects + sound_effect_str + "\n\n" + flag_line_context + line_context_str + "\n\n" + flag_original_txt + original_txt

    return input_txt

@st.cache_data
def create_prompt_for_tag_prompting():

    # 현재 파일의 디렉토리 경로
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # prompts 폴더 내의 파일 경로
    file_path_input1 = os.path.join(current_dir, '..', 'prompts', 'tag_promptingFSL_input1.txt')
    file_path_output1 = os.path.join(current_dir, '..', 'prompts', 'tag_promptingFSL_output1.txt')
    file_path_SYSTEM = os.path.join(current_dir, '..', 'prompts', 'tag_prompting_SYSTEM.txt')

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
def tag_prompting(input_txt):

    final_prompt = create_prompt_for_tag_prompting()
    model = generate_model(st.session_state["OPENAI_API_KEY"])

    chain = final_prompt | model

    result = chain.invoke({"input_txt": input_txt})

    finish_reason = result.response_metadata['finish_reason']

    # 출력 토큰 수 제한에 걸리지 않았을 경우, 그대로 출력
    if finish_reason != 'length':
        return result.content

    # 출력 토큰 수 제한으로 인해 끊겼을 경우, 이어서 생성 반복
    result_list = []
    result_list.append(result.content)
    while finish_reason == 'length':
        final_prompt.append(("ai", result.content))
        final_prompt.append(("human", "continue generation"))
        
        result = chain.invoke({"input_txt": input_txt})
        result_list.append(result.content)
        finish_reason = result.response_metadata['finish_reason']
    
    tag_prompted_text = "\n".join(result_list)

    return tag_prompted_text

def replace_korean_with_english(input_text, glossary):
    output_text = input_text

    # 각 용어에 대해 치환 수행
    for item in glossary:
        korean = item['Korean']
        english = item['English']
        output_text = output_text.replace(korean, english)

    return output_text




### Painting UI with Streamlit ###

st.title("번역 전 원문 가공")

col_left, col_right = st.columns(2)

with col_left:
    st.header("Step1 : 태그 프롬프팅")
    prepared = (
        (st.session_state["Info_1_Glossary"] != None) 
        and (st.session_state["Info_2_Sound_Effect"] != None) 
        and (st.session_state["Info_3_Line_Context"] != None)
    )
    button_tag_prompt = st.button("태그 프롬프팅 시작")
    if button_tag_prompt and prepared:
        input_text_for_tag_prompting = create_input_text_for_tag_prompting(st.session_state["Original_Text"], 
                                                                           st.session_state["Info_2_Sound_Effect"], 
                                                                           st.session_state["Info_3_Line_Context"])
        st.session_state["Tag_Prompted_Text"] = tag_prompting(input_text_for_tag_prompting)
    
    with st.container(height=600):
        st.write(st.session_state["Tag_Prompted_Text"])

with col_right:
    st.header("Step2 : 용어집 적용")
    button_apply_glossary = st.button("한글 용어 -> 영문으로 수정")
    if button_apply_glossary:
        st.session_state["Tag_Prompted_Text_with_glossary"] = replace_korean_with_english(st.session_state["Tag_Prompted_Text"], st.session_state["Info_1_Glossary"])
    
    with st.form("edit_preprocessed_text"):
        editing_preprocessed_text = st.text_area(label="용어집 적용",
                                                 label_visibility="collapsed",
                                                 value=st.session_state["Tag_Prompted_Text_with_glossary"],
                                                 height=600)
        submitted = st.form_submit_button("수정하기")
        if submitted:
            st.session_state["Tag_Prompted_Text_with_glossary"] = editing_preprocessed_text
            st.success("수정 완료!")



show_glossary, show_sound_effect, show_line_context = st.columns(3)

with show_glossary:
    st.subheader("용어집")
    st.json(st.session_state["Info_1_Glossary"], expanded=True)
with show_sound_effect:
    st.subheader("효과음 정보")
    st.json(st.session_state["Info_2_Sound_Effect"], expanded=True)
with show_line_context:
    st.subheader("대사 맥락정보")
    st.json(st.session_state["Info_3_Line_Context"], expanded=True)

    