import streamlit as st
from groq import Groq

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Skripsi Radar Si Anak Hukum", page_icon="🎓", layout="wide")

# 2. CSS Kustom dengan Tema Maroon
st.markdown("""
    <style>
    .main-card { 
        background: #800000; 
        padding: 2rem; 
        border-radius: 1rem; 
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); 
        border: 1px solid #600000; 
        color: #ffffff; 
        margin-bottom: 1rem;
    }
    .stButton>button { width: 100%; border-radius: 0.5rem; background-color: #800000; color: white; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# 3. Inisialisasi State
if 'is_premium' not in st.session_state: st.session_state.is_premium = False
if 'content_list' not in st.session_state: st.session_state.content_list = []
if 'pending_shortcut' not in st.session_state: st.session_state.pending_shortcut = None
if 'usage_count' not in st.session_state: st.session_state.usage_count = 0

# 4. Koneksi API
try:
    client = Groq(api_key=st.secrets["API_KEY"])
except Exception as e:
    st.error("API Key belum dikonfigurasi di Secrets!")
    st.stop()

# 5. Fungsi AI
def get_ai_response(prompt, context=""):
    full_prompt = f"Konteks Sebelumnya: {context}\n\nPermintaan: {prompt}" if context else prompt
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": full_prompt}],
        model="llama-3.1-8b-instant",
    )
    return chat_completion.choices[0].message.content

# 6. Sidebar Navigasi
st.sidebar.title("Navigasi")
menu = st.sidebar.radio("Menu", ["Generator Ide", "Riwayat", "Upgrade Premium"])

if st.sidebar.button("Hapus Riwayat Chat"):
    st.session_state.content_list = []
    st.rerun()

# 7. Halaman Utama
if menu == "Generator Ide":
    st.title("🎓 Skripsi Radar Si Anak Hukum")
    
    # Form Input
    with st.form("input_form"):
        col1, col2 = st.columns(2)
        with col1:
            bidang = st.text_input("Bidang Hukum")
            jenis = st.selectbox("Jenis", ["Normatif", "Empiris", "Socio-Legal", "Perbandingan Hukum"])
        with col2:
            isu = st.text_input("Isu Terkini")
            level = st.select_slider("Kedalaman Analisis", options=["Singkat", "Moderat", "Mendalam"])
        submitted = st.form_submit_button("Generate Ide")

    if submitted:
        prompt = f"Berikan 10 ide judul skripsi {bidang} ({jenis}) tentang {isu}. Kedalaman: {level}. Berikan dalam format nomor 1-10."
        response = get_ai_response(prompt)
        st.session_state.content_list.append({"role": "AI", "text": response})
        st.rerun()

    # Tampilkan Riwayat Konten
    for content in st.session_state.content_list:
        st.markdown(f'<div class="main-card">{content["text"]}</div>', unsafe_allow_html=True)

    # Shortcut Logic
    if st.session_state.content_list:
        st.write("---")
        st.subheader("💡 Tindakan Lanjutan")
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        if col_btn1.button("Kembangkan Judul"): st.session_state.pending_shortcut = "Kembangkan"
        if col_btn2.button("Alternatif judul"): st.session_state.pending_shortcut = "Alternatif"
        if col_btn3.button("Uji Dosen TTS"): st.session_state.pending_shortcut = "Uji Dosen"

        # Jika ada shortcut yang pending, tampilkan pilihan nomor
        if st.session_state.pending_shortcut:
            st.info(f"Pilih nomor judul (1-10) untuk: {st.session_state.pending_shortcut}")
            selected_num = st.number_input("Nomor Judul", min_value=1, max_value=10, step=1)
            if st.button("Proses Sekarang"):
                context = st.session_state.content_list[-1]['text']
                prompt = f"Fokus pada judul nomor {selected_num}. Permintaan: {st.session_state.pending_shortcut}."
                resp = get_ai_response(prompt, context)
                st.session_state.content_list.append({"role": "AI", "text": resp})
                st.session_state.pending_shortcut = None
                st.rerun()

        # Chat Interface
        st.subheader("💬 Tanya Lebih Lanjut")
        user_chat = st.chat_input("Tanyakan sesuatu tentang judul skripsi Anda...")
        if user_chat:
            context = st.session_state.content_list[-1]['text'] if st.session_state.content_list else ""
            resp = get_ai_response(user_chat, context)
            st.session_state.content_list.append({"role": "User", "text": user_chat})
            st.session_state.content_list.append({"role": "AI", "text": resp})
            st.rerun()

elif menu == "Riwayat":
    st.title("📜 Riwayat Lengkap")
    for item in st.session_state.content_list:
        st.write(f"**{item['role']}**: {item['text']}")

elif menu == "Upgrade Premium":
    st.title("💎 Upgrade ke Premium")
    st.write("Dapatkan akses fitur tanpa batas dan dukungan prioritas.")
    st.info("Pembayaran: DANA | 085922033291 | A/N: [EL** J******* E***** B******]")
    
    with st.expander("🔑 Aktivasi Premium"):
        code = st.text_input("Masukkan Kode Aktivasi", type="password")
        if st.button("Aktifkan"):
            if code == st.secrets.get("PREMIUM_KEY", "RAHASIA_123"):
                st.session_state.is_premium = True
                st.success("Berhasil! Akun Anda kini Premium.")
            else:
                st.error("Kode salah.")
