import streamlit as st
from groq import Groq
import requests

st.set_page_config(page_title="Skripsi Radar Si Anak Hukum", page_icon="🎓", layout="wide")

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

if 'is_premium' not in st.session_state: st.session_state.is_premium = False
if 'content_list' not in st.session_state: st.session_state.content_list = []
if 'pending_shortcut' not in st.session_state: st.session_state.pending_shortcut = None
if 'usage_count' not in st.session_state: st.session_state.usage_count = 0

try:
    client = Groq(api_key=st.secrets["API_KEY"])
except Exception as e:
    st.error("API Key belum dikonfigurasi di Secrets!")
    st.stop()

def send_telegram_notification(message):
    """Fungsi untuk mengirim notifikasi ke Telegram"""
    token = st.secrets.get("TELEGRAM_TOKEN")
    chat_id = st.secrets.get("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        params = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
        try:
            requests.get(url, params=params)
        except:
            pass

def check_usage_and_generate(prompt, context=""):
    """Fungsi untuk mengecek kuota dan memanggil AI"""
    if not st.session_state.is_premium and st.session_state.usage_count >= 3:
        st.error("⚠️ **Kuota Gratis Anda telah habis!** Silakan buka menu 'Upgrade Premium' untuk akses tanpa batas.")
        return None
    
    full_prompt = f"Konteks Sebelumnya: {context}\n\nPermintaan: {prompt}" if context else prompt
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": full_prompt}],
        model="llama-3.1-8b-instant",
    )
    response = chat_completion.choices[0].message.content
    
    if not st.session_state.is_premium:
        st.session_state.usage_count += 1
    
    return response

st.sidebar.title("Navigasi")
menu = st.sidebar.radio("Menu", ["Generator Ide", "Riwayat", "Upgrade Premium"])

if st.sidebar.button("Hapus Riwayat Chat"):
    st.session_state.content_list = []
    st.session_state.usage_count = 0
    st.rerun()

if menu == "Generator Ide":
    st.title("🎓 Skripsi Radar Si Anak Hukum")
    
    if not st.session_state.is_premium:
        sisa = max(0, 3 - st.session_state.usage_count)
        st.info(f"**Kuota Gratis Anda:** {sisa} / 3 tersisa")
    else:
        st.success("✅ Akun Premium Aktif (Tanpa Batas)")
    
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
        response = check_usage_and_generate(prompt)
        if response:
            st.session_state.content_list.append({"role": "AI", "text": response})
            st.rerun()

    for content in st.session_state.content_list:
        st.markdown(f'<div class="main-card">{content["text"]}</div>', unsafe_allow_html=True)

    if st.session_state.content_list:
        st.write("---")
        st.subheader("💡 Tindakan Lanjutan")
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        if col_btn1.button("Kembangkan Judul"): st.session_state.pending_shortcut = "Kembangkan"
        if col_btn2.button("Alternatif judul"): st.session_state.pending_shortcut = "Alternatif"
        if col_btn3.button("Uji Dosen TTS"): st.session_state.pending_shortcut = "Uji Dosen"

        if st.session_state.pending_shortcut:
            st.info(f"Pilih nomor judul (1-10) untuk: {st.session_state.pending_shortcut}")
            selected_num = st.number_input("Nomor Judul", min_value=1, max_value=10, step=1)
            if st.button("Proses Sekarang"):
                context = st.session_state.content_list[-1]['text']
                prompt = f"Fokus pada judul nomor {selected_num}. Permintaan: {st.session_state.pending_shortcut}."
                resp = check_usage_and_generate(prompt, context)
                if resp:
                    st.session_state.content_list.append({"role": "AI", "text": resp})
                    st.session_state.pending_shortcut = None
                    st.rerun()

        st.subheader("💬 Tanya Lebih Lanjut")
        user_chat = st.chat_input("Tanyakan sesuatu tentang judul skripsi Anda...")
        if user_chat:
            context = st.session_state.content_list[-1]['text'] if st.session_state.content_list else ""
            resp = check_usage_and_generate(user_chat, context)
            if resp:
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
                send_telegram_notification(f"🔔 <b>Ada Aktivasi Premium Baru!</b>\nKode yang digunakan: {code}")
                st.success("Berhasil! Akun Anda kini Premium.")
                st.rerun()
            else:
                st.error("Kode salah.")
