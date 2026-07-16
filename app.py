import streamlit as st
from groq import Groq

# Pengaturan halaman
st.set_page_config(page_title="Skripsi Radar Pro", page_icon="🎓", layout="centered")

st.markdown("""
    <style>
    .main-card { background: #800000; padding: 1.5rem; border-radius: 1rem; color: #ffffff; margin-bottom: 1rem; }
    .history-card { background: #fcf2f2; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; border-left: 4px solid #800000; color: #333333; }
    .stButton>button { width: 100%; border-radius: 0.5rem; background-color: #800000; color: white; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# Inisialisasi State
if 'is_premium' not in st.session_state: st.session_state.is_premium = False
if 'usage_count' not in st.session_state: st.session_state.usage_count = 0
if 'history' not in st.session_state: st.session_state.history = []
if 'content_list' not in st.session_state: st.session_state.content_list = []
if 'active_shortcut' not in st.session_state: st.session_state.active_shortcut = None

try:
    client = Groq(api_key=st.secrets["API_KEY"])
except:
    st.error("API Key belum disetting di Secrets!")
    st.stop()

def get_ai_response(prompt, context=""):
    full_prompt = f"Konteks Sebelumnya: {context}\n\nPermintaan: {prompt}" if context else prompt
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": full_prompt}],
        model="llama-3.1-8b-instant",
    )
    return chat_completion.choices[0].message.content

# Sidebar
if not st.session_state.is_premium:
    with st.sidebar.expander("🔑 Aktivasi Premium"):
        activation_code = st.text_input("Kode Aktivasi", type="password")
        if st.button("Aktifkan"):
            if activation_code == st.secrets.get("PREMIUM_KEY", "RAHASIA_123"):
                st.session_state.is_premium = True
                st.rerun()

menu = st.sidebar.radio("Navigasi", ["Generator Ide", "Riwayat", "Upgrade Premium"])

if menu == "Generator Ide":
    st.title("🎓 Skripsi Radar")
    
    # Form Input
    with st.form("input_form"):
        bidang = st.text_input("Bidang Hukum")
        col1, col2 = st.columns(2)
        with col1:
            jenis = st.selectbox("Jenis", ["Normatif", "Empiris", "Socio-Legal"])
        with col2:
            isu = st.text_input("Isu Terkini")
        submitted = st.form_submit_button("Generate Ide")

    if submitted:
        if st.session_state.is_premium or st.session_state.usage_count < 3:
            prompt = f"Berikan 5 ide judul skripsi {bidang} ({jenis}) tentang {isu}."
            response = get_ai_response(prompt)
            st.session_state.content_list.append(f"### Ide Baru ({bidang})\n{response}")
            if not st.session_state.is_premium: st.session_state.usage_count += 1
        else:
            st.warning("Limit gratis habis!")

    # Menampilkan semua konten yang sudah digenerate (Bubble Chat Style)
    for content in st.session_state.content_list:
        st.markdown(f'<div class="main-card">{content}</div>', unsafe_allow_html=True)
        
    # Area Shortcut
    if len(st.session_state.content_list) > 0:
        st.markdown("---")
        st.subheader("💡 Tindakan Lanjutan")
        
        c1, c2 = st.columns(2)
        if c1.button("Kembangkan Judul"):
            st.session_state.active_shortcut = "Kembangkan"
        if c2.button("Uji Dosen TTS"):
            st.session_state.active_shortcut = "Uji Dosen"

        # Form Pemrosesan Shortcut
        if st.session_state.active_shortcut:
            with st.container():
                st.info(f"Opsi: **{st.session_state.active_shortcut}**")
                target_num = st.number_input("Pilih nomor judul (1-5)", 1, 5, 1)
                
                if st.button("Jalankan Proses"):
                    with st.spinner("Memproses..."):
                        context = st.session_state.content_list[-1]
                        prompts = {
                            "Kembangkan": f"Kembangkan detail untuk judul nomor {target_num} dari daftar: {context}",
                            "Uji Dosen": f"Simulasikan pertanyaan dosen untuk judul nomor {target_num} dari daftar: {context}"
                        }
                        resp = get_ai_response(prompts[st.session_state.active_shortcut], context)
                        st.session_state.content_list.append(f"### Hasil {st.session_state.active_shortcut} (Judul {target_num})\n{resp}")
                        st.session_state.active_shortcut = None
                        st.rerun()

elif menu == "Riwayat":
    st.title("📜 Riwayat")
    # Tampilkan riwayat di sini

elif menu == "Upgrade Premium":
    st.title("💎 Upgrade ke Premium")
    st.link_button("Konfirmasi via WhatsApp", "https://wa.me/6285922033291")
