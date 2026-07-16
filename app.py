import streamlit as st
from groq import Groq

# st.set_page_config(page_title="Skripsi Radar Pro", page_icon="🎓", layout="wide")

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
    .history-card {
        background: #fcf2f2;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #800000;
        color: #333333;
    }
    .stButton>button { width: 100%; border-radius: 0.5rem; background-color: #800000; color: white; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

if 'is_premium' not in st.session_state: st.session_state.is_premium = False
if 'usage_count' not in st.session_state: st.session_state.usage_count = 0
if 'history' not in st.session_state: st.session_state.history = []
if 'content_list' not in st.session_state: st.session_state.content_list = []
if 'last_input' not in st.session_state: st.session_state.last_input = ""
if 'active_shortcut' not in st.session_state: st.session_state.active_shortcut = None

try:
    client = Groq(api_key=st.secrets["API_KEY"])
except:
    st.error("API Key belum disetting di Secrets!")
    st.stop()

def get_ai_response(prompt, context=""):
    full_prompt = f"Konteks: {context}\n\nPermintaan: {prompt}" if context else prompt
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": full_prompt}],
        model="llama-3.1-8b-instant",
    )
    return chat_completion.choices[0].message.content

def can_access():
    if st.session_state.is_premium: return True
    return st.session_state.usage_count < 3

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

if st.session_state.is_premium:
    st.sidebar.success("Status: Member Premium 💎")
else:
    remaining = max(0, 3 - st.session_state.usage_count)
    st.sidebar.info(f"Sisa akses gratis: {remaining} kali")

menu = st.sidebar.radio("Navigasi", ["Generator Ide", "Riwayat", "Upgrade Premium"])

if menu == "Generator Ide":
    st.title("🎓 Skripsi Radar")
    
    with st.form("input_form"):
        col1, col2 = st.columns(2)
        with col1:
            bidang = st.text_input("Bidang Hukum")
            jenis = st.selectbox("Jenis", ["Normatif", "Empiris", "Socio-Legal", "Perbandingan Hukum"])
        with col2:
            isu = st.text_input("Isu Terkini")
            level = st.select_slider("Kedalaman", options=["Umum", "Moderat", "Niche"])
        submitted = st.form_submit_button("Generate Judul")

    if submitted:
        if can_access():
            prompt = f"Berikan 5 ide judul skripsi {bidang} ({jenis}) tentang {isu}. Kedalaman: {level}."
            response = get_ai_response(prompt)
            st.session_state.content_list = [response] 
            st.session_state.last_input = f"{bidang} - {isu}"
            st.session_state.history.append({"tool": "Generator", "input": st.session_state.last_input, "result": response})
            if not st.session_state.is_premium: st.session_state.usage_count += 1
        else:
            st.warning("Limit gratis habis!")

    # Menampilkan konten list
    for content in st.session_state.content_list:
        st.markdown(f'<div class="main-card">{content}</div>', unsafe_allow_html=True)
        
    if len(st.session_state.content_list) > 0:
        st.write("---")
        st.subheader("💡 Tindakan Lanjutan")
        
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        if col_btn1.button("Kembangkan Judul"):
            st.session_state.active_shortcut = "Kembangkan"
            st.rerun()
        
        if col_btn3.button("Uji Dosen TTS"):
            st.session_state.active_shortcut = "Uji Dosen"
            st.rerun()

        if st.session_state.active_shortcut:
            st.write("---")
            with st.container():
                st.info(f"Opsi dipilih: **{st.session_state.active_shortcut}**")
                target_num = st.number_input("Judul nomor berapa yang ingin kamu proses? (1-5)", min_value=1, max_value=5, value=1)
                
                c_run, c_cancel = st.columns([1, 4])
                if c_run.button("Jalankan"):
                    with st.spinner(f"Memproses {st.session_state.active_shortcut}..."):
                        context = st.session_state.content_list[-1]
                        prompts = {
                            "Kembangkan": f"Kembangkan detail skripsi untuk judul nomor {target_num} dari daftar ini: {context}",
                            "Uji Dosen": f"Berikan simulasi pertanyaan kritis dosen penguji khusus untuk judul nomor {target_num} dari daftar ini: {context}"
                        }
                        
                        resp = get_ai_response(prompts[st.session_state.active_shortcut], context)
                        # Appending to list instead of replacing
                        st.session_state.content_list.append(f"### Hasil {st.session_state.active_shortcut} (Judul {target_num})\n{resp}")
                        st.session_state.active_shortcut = None 
                        st.rerun()
                
                if c_cancel.button("Batal"):
                    st.session_state.active_shortcut = None
                    st.rerun()

elif menu == "Riwayat":
    st.title("📜 Riwayat Lengkap")
    if st.session_state.history:
        for item in reversed(st.session_state.history): 
            st.markdown(f"""
                <div class="history-card">
                    <strong>{item['tool']}</strong>: {item['input']}<br>
                    {str(item['result']).replace('\n', '<br>')}
                </div>
            """, unsafe_allow_html=True)

elif menu == "Upgrade Premium":
    st.title("💎 Upgrade ke Premium")
    st.markdown("- **E-Wallet:** DANA | 085922033291")
    st.link_button("Konfirmasi via WhatsApp", "https://wa.me/6285922033291")
