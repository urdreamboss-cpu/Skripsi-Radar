import streamlit as st
import google.generativeai as genai

# Konfigurasi Halaman
st.set_page_config(page_title="Skripsi Radar Pro", page_icon="🎓", layout="wide")

# CSS Kustom
st.markdown("""
    <style>
    .main-card { background: white; padding: 2rem; border-radius: 1rem; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); border: 1px solid #e2e8f0; }
    .stButton>button { width: 100%; border-radius: 0.5rem; background-color: #2563eb; color: white; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# Sidebar Login
st.sidebar.title("Login Akses")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

# Konfigurasi AI
try:
    genai.configure(api_key=st.secrets["API_KEY"])
    model_text = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("API Key belum disetting di Secrets!")
    st.stop()

# Navigasi Menu
menu = st.sidebar.radio("Navigasi", ["Generator Ide", "Thesis Lab", "Riwayat", "Upgrade Premium"])

if 'history' not in st.session_state: 
    st.session_state.history = []

# Logika Menu
if menu == "Generator Ide":
    st.title("🎓 Generator Judul Skripsi Hukum")
    st.write("Isi parameter di bawah agar AI memberikan hasil yang sangat spesifik.")
    
    with st.form("input_form"):
        col1, col2 = st.columns(2)
        with col1:
            bidang = st.text_input("Bidang Hukum Diminati", placeholder="Contoh: Hukum Pidana, Hukum Tata Negara")
            jenis = st.selectbox("Jenis Penelitian", ["Normatif", "Empiris", "Socio-Legal", "Perbandingan Hukum"])
        with col2:
            isu = st.text_input("Isu/Fenomena Terkini", placeholder="Contoh: UU ITE, Kecerdasan Buatan, Korupsi")
            level = st.select_slider("Level Kedalaman Topik", options=["Umum & Aman", "Moderat", "Niche & Unik"])
        
        submitted = st.form_submit_button("Generate Judul")

    if submitted:
        with st.spinner("AI sedang meriset regulasi dan isu terkini..."):
            prompt = f"""
            Anda adalah seorang Profesor Hukum. Buatkan 5 ide judul skripsi yang sangat spesifik, akademis, dan inovatif berdasarkan:
            - Bidang: {bidang}
            - Isu/Fenomena: {isu}
            - Jenis Penelitian: {jenis}
            - Kedalaman: {level}
            
            Berikan judul yang menarik untuk sidang skripsi.
            """
            response = model_text.generate_content(prompt)
            st.markdown(f'<div class="main-card">{response.text}</div>', unsafe_allow_html=True)
            st.session_state.history.append(f"Generator ({bidang}, {jenis}): {response.text}")

elif menu == "Thesis Lab":
    st.title("🛠 Thesis Lab")
    sub_tool = st.selectbox("Pilih Alat:", ["Kembangkan Judul", "10 Alternatif", "Persempit Sub-topik", "Uji Dosen TTS"])
    judul_input = st.text_input("Masukkan judul Anda:")

    if st.button("Jalankan Tools"):
        with st.spinner("AI sedang bekerja..."):
            if sub_tool == "Kembangkan Judul":
                prompt = f"Kembangkan judul berikut menjadi kerangka latar belakang bab 1 yang kuat: {judul_input}"
            elif sub_tool == "10 Alternatif":
                prompt = f"Berikan 10 variasi judul lain yang lebih spesifik dari: {judul_input}"
            elif sub_tool == "Uji Dosen TTS":
                prompt = f"Anda adalah Dosen Pembimbing yang kritis (Killer). Berikan kritik tajam, temukan celah metodologi, dan berikan masukan perbaikan untuk judul: {judul_input}"
            elif sub_tool == "Persempit Sub-topik":
                prompt = f"Berikan 3 sub-topik penelitian yang lebih spesifik dan tajam untuk judul: {judul_input}"
            
            res = model_text.generate_content(prompt)
            st.markdown(f'<div class="main-card">{res.text}</div>', unsafe_allow_html=True)
            st.session_state.history.append(f"{sub_tool} ({judul_input}): {res.text}")

elif menu == "Riwayat":
    st.title("📜 Riwayat")
    if st.session_state.history:
        for item in st.session_state.history:
            st.write("- " + item)
    else:
        st.write("Belum ada riwayat.")

elif menu == "Upgrade Premium":
    st.title("💎 Upgrade ke Premium")
    st.write("Dapatkan akses penuh ke fitur riset lanjutan, analisis mendalam, dan dukungan prioritas.")
    
    st.subheader("💳 Detail Pembayaran")
    st.markdown("""
    Silakan melakukan transfer ke rekening berikut:
    - **Bank:** BRI
    - **Nomor Rekening:** 068801022550502
    - **Atas Nama:** ELSA JAINIFER EUNIKE BAGARAI
    - **Jumlah:** Rp 25.000
    """)

    st.info("Setelah transfer, silakan kirim bukti pembayaran ke WhatsApp Admin agar akses segera diaktifkan.")
    st.link_button("Konfirmasi via WhatsApp", "https://wa.me/6285922033291?text=Halo%20Admin,%20saya%20sudah%20transfer%20untuk%20Skripsi%20Radar.")
