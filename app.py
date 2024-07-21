from dotenv import load_dotenv
import os
from pandasai import SmartDataframe
import pandas as pd
from pandasai.llm import BambooLLM
from pandasai.connectors import PandasConnector
import streamlit as st

load_dotenv()

os.environ["PANDASAI_API_KEY"] = os.getenv('PANDASAI_API_KEY')

Prompt_Template = """
Sen borsa yatırımcıları için bir asistansın ve soruyu yalnızca aşağıdaki bağlama dayanarak cevapla:

{context}

Yukarıdaki bağlama dayanarak soruyu cevapla: {question}
"""

llm = BambooLLM()

transictions = pd.read_csv("data/transaction.csv")

field_descriptions_transiction = {
    "İşlem":"Yatırımcının belirtilen hisseyi aldığını ya da sattığını gösterir.",    
    "Hisse Senedi":"Yatırımcının işlem yaptığı hisse kodudur.",
    "Adet":"İşlem yapılan hissenin kaç adet yapıldığını gösterir",
    "Fiyat":"İşlem yapılan hissede hangi fiyattan işlem yapıldığını gösterir",
    "Tarih":"İşlemin yapıldığı tarih",
    "Sektör":"İşlem yapılan hissenin ait olduğu şirketin sektörünü belirtir.",
}

config = {
    'llm': llm,
    'save_charts': False,
    'save_charts_path': 'exports/charts',
    'open_charts': False,
    'max_retries': 2}


transictions_connector = PandasConnector({"original_df": transictions}, field_descriptions=field_descriptions_transiction)

sdf = SmartDataframe(transictions_connector,name='transictions',description='yatırımcının geçmişte yaptığı işlemler',config=config)

transictions = SmartDataframe(
    sdf,
    config={
        "llm":llm,
        "save_charts": True,
        "save_charts_path": "exports/charts"
    }
)

def ai_query(user_input):
    response = get_response_from_PandasAi(user_input)
    return response


def get_response_from_PandasAi(user_input):
    return sdf.chat(user_input)
    
st.set_page_config(page_title="AKbulut Chatbot", page_icon="assets/communication.png")

# Streamlit UI setup
st.markdown("<h1 style='color: red; text-align: center;'>AKbulut Chatbot</h1>", unsafe_allow_html=True)

# Custom CSS for the background and message colors
st.markdown(
    """
    <style>
    .stApp {
        background-color: black;
    }
    .user-message {
        background-color: white;
        border-radius: 8px;
        padding: 10px;
        margin: 5px 0;
        margin-left: auto;
        color: red;
        width: fit-content;
        max-width: 80%;
    }
    .bot-message {
        background-color: red;
        border-radius: 8px;
        padding: 10px;
        margin: 5px 0;
        color: white;
        width: fit-content;
        max-width: 80%;
    }
    .bot-message img {
    position: absolute;
    bottom: 10px;
    left: -60px; /* Resmin konuşma balonunun soluna çıkıntı yapmasını sağlamak için negatif bir değer kullanın */
    width: 30px;
    }
    
    </style>
    """,
    unsafe_allow_html=True
)


if 'user_responses' not in st.session_state:
    st.session_state['user_responses'] = ["Merhaba"]
if 'bot_responses' not in st.session_state:
    st.session_state['bot_responses'] = ["Merhaba, ben dijital asistanınız AKbulut. Size nasıl yardımcı olabilirim?"]

input_container = st.container()
response_container = st.container()

user_input = st.text_input("AKbulut uygulamasına ileti gönder", "", key="input")

with response_container:
    if user_input:
        response = ai_query(user_input)
        st.session_state.user_responses.append(user_input)
        st.session_state.bot_responses.append(response)

    if st.session_state['bot_responses']:
        for i in range(len(st.session_state['bot_responses'])):
            st.markdown(f'<div class="user-message">{st.session_state["user_responses"][i]}</div>', unsafe_allow_html=True)
            col1, col2 = st.columns([1, 9])
            with col1:
                st.image("assets/cloud_icon.png", width=30, use_column_width=True, clamp=True, output_format='auto')
            with col2:
                bot_response = st.session_state["bot_responses"][i]
                if isinstance(bot_response, str) and ".png" in bot_response:
                    st.image(bot_response, use_column_width=True)
                else:
                    st.markdown(f'<div class="bot-message">{bot_response}</div>', unsafe_allow_html=True)


with input_container:
    display_input = user_input  
