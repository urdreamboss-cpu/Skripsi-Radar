import streamlit as st
from groq import Groq

# Konfigurasi Halaman
st.set_page_config(page_title="Skripsi Radar", page_icon="🎓", layout="centered")

# Inisialisasi Session State
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'usage_count' not in st.session_state:
    st.session_state.usage_count = 0

# Styling CSS - Pastikan tidak ada tanda # di depan st.markdown
st.markdown("""
    <style>
    .main-card { background: #ffffff; padding: 1.5rem; border-radius: 1rem; border-left: 5px solid #800000; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .stButton>button { width: 100%; border-radius: 0.5rem; background-color: #800000; color: white; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# Inisialisasi Client
try:
    client = Groq(api_key=st.secrets["API_KEY"])
except Exception as e:
    st.error("API Key belum dikonfigurasi dengan benar di Secrets!")
    st.stop()

def get_ai_response(messages):
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama-3.1-8b-instant",
    )
    return chat_completion.choices[0].message.content

# Sidebar Menu
menu = st.sidebar.radio("Navigasi", ["Generator Ide", "Upgrade Premium"])

if menu == "Generator Ide":
    st.title("🎓 Skripsi Radar")
    
    with st.form("input_form"):
        bidang = st.text_input("Bidang Hukum")
        col1, col2 = st.columns(2)
        with col1:
            jenis = st.selectbox("Jenis", ["Normatif", "Empiris", "Socio-Legal"])
        with col2:
            kedalaman = st.selectbox("Kedalaman Analisis", ["Singkat", "Menengah", "Mendalam (Detail)"])
        isu = st.text_input("Isu Terkini")
        submitted = st.form_submit_button("Generate Ide Skripsi")

    if submitted:
        if st.session_state.usage_count < 10:
            prompt = f"Berikan 10 ide judul skripsi {bidang} ({jenis}) tentang {isu} dengan kedalaman {kedalaman}."
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.spinner("AI sedang meriset..."):
                response = get_ai_response(st.session_state.messages)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.session_state.usage_count += 1
        else:
            st.warning("Limit gratis habis!")

    st.divider()
    st.subheader("💬 Diskusi Lanjutan")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Tanyakan sesuatu tentang judul skripsi Anda..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            response = get_ai_response(st.session_state.messages)
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

elif menu == "Upgrade Premium":
    st.title("💎 Upgrade ke Premium")
    st.write("Dapatkan akses fitur tanpa batas dan dukungan prioritas.")
    st.link_button("Konfirmasi via WhatsApp", "https://wa.me/6285922033291")

# Tombol untuk mereset sesi chat jika perlu
if st.sidebar.button("Hapus Riwayat Chat"):
    st.session_state.messages = []
    st.session_state.usage_count = 0
    st.rerun()
