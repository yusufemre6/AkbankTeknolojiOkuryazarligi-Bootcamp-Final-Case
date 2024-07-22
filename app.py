from dotenv import load_dotenv
import os
from pandasai import SmartDataframe
from pandasai import SmartDatalake
import pandas as pd
from pandasai.llm import BambooLLM
from pandasai.connectors import PandasConnector
import streamlit as st
import re

load_dotenv()

os.environ["PANDASAI_API_KEY"] = os.getenv('PANDASAI_API_KEY')

llm = BambooLLM(api_key="$2a$10$2P0Y90vb4DpY4u97.cxhoe8mQRJz0ECYwBkrJKyXpF66csxcWIMbq")

transictions = pd.read_csv("data/transaction.csv")
porfolio = pd.read_csv("data/portfolio.csv")
bist100 = pd.read_csv("data/bist100_stocks_2020_2024.csv")

transictions = pd.DataFrame(transictions)
porfolio = pd.DataFrame(porfolio)
bist100 = pd.DataFrame(bist100)


field_descriptions_transiction = {
    "İşlem":"Yatırımcının belirtilen hisseyi aldığını ya da sattığını gösterir.",    
    "Hisse Senedi":"Yatırımcının işlem yaptığı hisse kodudur.",
    "Adet":"İşlem yapılan hissenin kaç adet yapıldığını gösterir",
    "Fiyat":"İşlem yapılan hissede hangi fiyattan işlem yapıldığını gösterir",
    "Tarih":"İşlemin yapıldığı tarih",
    "Sektör":"İşlem yapılan hissenin ait olduğu şirketin sektörünü belirtir.",
}

field_descriptions_porfolio = {
    "Hisse Senedi":"Porföyde bulunan hisse senedinin adını verir.",
    "Adet":"Satırda bulunan hisse senedinin portföyde kaç adet olduğunu gösterir.",
    "Alış Fiyatı":"Satırda bulunan hisse senedinin alış fiyatını gösterir. ",
    "Sektör":"Alınan hisse senedinin hangi sektörden şirkete ait olduğunu gösterir."
}

field_descriptions_bist100 = {
    "Date": "Verinin kaydedildiği tarihi gösterir.",
    "Open": "Borsa açılışında hisse senedinin fiyatını gösterir.",
    "High": "Gün içerisindeki en yüksek hisse senedi fiyatını gösterir.",
    "Low": "Gün içerisindeki en düşük hisse senedi fiyatını gösterir.",
    "Close": "Borsa kapanışında hisse senedinin fiyatını gösterir.",
    "Volume": "Gün içerisinde işlem gören hisse senedi adedini gösterir.",
    "Dividends": "Hisse senedi için ödenen temettü miktarını gösterir.",
    "Stock Splits": "Hisse senedinde yapılan bölünme işlemlerini gösterir.",
    "Ticker": "Hisse senedinin sembolünü (kısa kodunu) gösterir."
}

config = {
    'llm': llm,
    'save_charts': False,
    'save_charts_path': 'exports/charts',
    'open_charts': True,
    'max_retries': 5}


transictions_connector = PandasConnector({"original_df": transictions}, field_descriptions=field_descriptions_transiction)
porfolio_connector = PandasConnector({"original_df": porfolio}, field_descriptions=field_descriptions_porfolio)
bist100_connector = PandasConnector({"original_df": bist100}, field_descriptions=field_descriptions_bist100)

sdf_transactions = SmartDataframe(transictions_connector,name='transictions',description='yatırımcının geçmişte yaptığı işlemler',config=config)
sdf_portfolio = SmartDataframe(porfolio_connector,name='portfolio',description='yatırımcının şu anda bulunun hisselerinin portföyü',config=config)
sdf_bist100 = SmartDataframe(bist100_connector,name='bist100',description='yatırımcının yatırım yapabileceği bist100 hisse senetleri',config=config)


def ai_query(user_input):
    
    # Regex pattern
    pattern = r'#\b[A-Z]{5}\b|\d+|\b(al|sat)\b'
    # Regex ile eşleşmeleri bul
    matches = [match.group() for match in re.finditer(pattern, user_input)]
    # Eşleşme olup olmadığını kontrol et
    if matches:
        response = "{} hisse senedinden {} adet {} işlemi yapıldı.".format(matches[0],matches[1],matches[2])
    else:
        pattern = r'\btavsiye\b'
        # Regex ile eşleşmeleri bul
        matches = re.search(pattern, user_input)
        # Eşleşme olup olmadığını kontrol et
        if matches:
            response = "Geçmiş yatırımlarınıza göre Holding sektöründen hisse senetlerine yatırım yapabilirsiniz."
        else:
            response = get_response_from_PandasAi(user_input)
    return response


def get_response_from_PandasAi(user_input):
    return sdf_transactions.chat(user_input)
    
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
