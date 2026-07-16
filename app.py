import streamlit as st
from groq import Groq

st.set_page_config(page_title="Skripsi Radar Pro", page_icon="🎓", layout="wide")

# CSS Kustom
st.markdown("""
    <style>
    .main-card { 
        background: white; 
        padding: 2rem; 
        border-radius: 1rem; 
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); 
        border: 1px solid #e2e8f0; 
        color: #1e293b; 
    }
    .stButton>button { width: 100%; border-radius: 0.5rem; background-color: #2563eb; color: white; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# --- Inisialisasi State ---
if 'is_premium' not in st.session_state: st.session_state.is_premium = False
if 'usage_count' not in st.session_state: st.session_state.usage_count = 0
if 'history' not in st.session_state: st.session_state.history = []

# --- Konfigurasi AI & Secrets ---
try:
    client = Groq(api_key=st.secrets["API_KEY"])
except:
    st.error("API Key belum disetting!")
    st.stop()

# --- Sidebar & Login / Aktivasi ---
st.sidebar.title("Login Akses")
# Fitur Aktivasi Premium
if not st.session_state.is_premium:
    with st.sidebar.expander("🔑 Aktivasi Premium"):
        activation_code = st.text_input("Masukkan Kode Aktivasi", type="password")
        if st.button("Aktifkan"):
            if activation_code == st.secrets.get("PREMIUM_KEY", "RAHASIA_123"):
                st.session_state.is_premium = True
                st.success("Berhasil! Akun Anda kini Premium.")
                st.rerun()
            else:
                st.error("Kode salah.")

# Informasi Status
if st.session_state.is_premium:
    st.sidebar.success("Status: Member Premium 💎")
else:
    remaining = max(0, 3 - st.session_state.usage_count)
    st.sidebar.info(f"Sisa akses gratis: {remaining} kali")

# --- Helper Fungsi ---
def get_ai_response(prompt):
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant",
    )
    return chat_completion.choices[0].message.content

def can_access():
    if st.session_state.is_premium: return True
    if st.session_state.usage_count < 3: return True
    return False

# --- Menu Navigasi ---
menu = st.sidebar.radio("Navigasi", ["Generator Ide", "Thesis Lab", "Riwayat", "Upgrade Premium"])

if menu == "Generator Ide":
    st.title("🎓 Generator Judul Skripsi Hukum")
    
    with st.form("input_form"):
        col1, col2 = st.columns(2)
        with col1:
            bidang = st.text_input("Bidang Hukum Diminati")
            jenis = st.selectbox("Jenis Penelitian", ["Normatif", "Empiris", "Socio-Legal", "Perbandingan Hukum"])
        with col2:
            isu = st.text_input("Isu/Fenomena Terkini")
            level = st.select_slider("Level Kedalaman", options=["Umum & Aman", "Moderat", "Niche & Unik"])
        
        submitted = st.form_submit_button("Generate Judul")

    if submitted:
        if can_access():
            with st.spinner("AI sedang meriset..."):
                prompt = f"Berikan 5 ide judul skripsi {bidang} ({jenis}) tentang {isu}. Kedalaman: {level}."
                response = get_ai_response(prompt)
                st.markdown(f'<div class="main-card">{response}</div>', unsafe_allow_html=True)
                st.session_state.history.append(f"Generator: {bidang} - {isu}")
                if not st.session_state.is_premium: st.session_state.usage_count += 1
        else:
            st.warning("Limit gratis habis! Silakan Upgrade ke Premium.")

elif menu == "Thesis Lab":
    st.title("🛠 Thesis Lab")
    sub_tool = st.selectbox("Pilih Alat:", ["Kembangkan Judul", "10 Alternatif", "Uji Dosen TTS"])
    judul_input = st.text_input("Masukkan judul Anda:")

    if st.button("Jalankan Tools"):
        if can_access():
            with st.spinner("AI sedang bekerja..."):
                prompt = f"{sub_tool} untuk judul: {judul_input}"
                response = get_ai_response(prompt)
                st.markdown(f'<div class="main-card">{response}</div>', unsafe_allow_html=True)
                st.session_state.history.append(f"{sub_tool}: {judul_input}")
                if not st.session_state.is_premium: st.session_state.usage_count += 1
        else:
            st.warning("Limit gratis habis! Silakan Upgrade ke Premium.")

elif menu == "Riwayat":
    st.title("📜 Riwayat")
    for item in st.session_state.history: st.write("- " + item)

elif menu == "Upgrade Premium":
    st.title("💎 Upgrade ke Premium")
    st.markdown("""
    - **E-Wallet:** DANA | 085922033291 (E*S* J******* E***** BA*****)
    - **Jumlah:** Rp 25.000
    """)
    st.link_button("Konfirmasi via WhatsApp", "[https://wa.me/6285922033291?text=Halo%20Admin,%20saya%20sudah%20transfer%20untuk%20Skripsi%20Radar](https://wa.me/6285922033291?text=Halo%20Admin,%20saya%20sudah%20transfer%20untuk%20Skripsi%20Radar).")
