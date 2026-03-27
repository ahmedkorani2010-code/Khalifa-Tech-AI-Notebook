import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# 1. إعدادات الواجهة (لون فاتح وبسيط)
st.set_page_config(page_title="Notebook-KSIT AI", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .stButton>button { border-radius: 20px; background-color: #f8f9fa; color: #1f77b4; border: 1px solid #1f77b4; }
    </style>
    """, unsafe_allow_html=True)

# 2. إدخال مفتاح الـ API (تأكد من وضعه هنا)
API_KEY = "AIzaSyBtRA83TXyq93Gq997Or0owYlufh5AeR4Y" 

# إعداد النموذج مع معالجة خطأ الـ NotFound
try:
    genai.configure(api_key=API_KEY)
    # جربنا 'gemini-1.5-flash' وإذا لم يعمل سنستخدم 'gemini-pro'
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"خطأ في الإعداد: {e}")

# 3. دالة استخراج النص
def extract_text(files):
    text = ""
    for file in files:
        if file.type == "application/pdf":
            reader = PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
        else:
            text += file.read().decode("utf-8")
    return text

# 4. واجهة البرنامج
st.title("🖥️ مساعد طلاب معهد الشيخ خليفة")
st.info("قسم تقنيات الحاسوب - نظام التعلم الذكي")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "context" not in st.session_state:
    st.session_state.context = ""

# القائمة الجانبية
with st.sidebar:
    st.header("📂 الملفات")
    uploaded_files = st.file_uploader("ارفع مذكراتك (PDF/TXT)", accept_multiple_files=True, type=['pdf', 'txt'])
    
    if uploaded_files:
        st.session_state.context = extract_text(uploaded_files)
        st.success("تمت قراءة الملفات!")
    
    st.divider()
    
    if st.button("📝 ملخص سريع"):
        if st.session_state.context:
            with st.spinner("جاري التلخيص..."):
                res = model.generate_content(f"لخص الآتي باحترافية: {st.session_state.context[:10000]}")
                st.write(res.text)
        else:
            st.warning("ارفع ملفاً أولاً")

    if st.button("❓ توليد كويز"):
        if st.session_state.context:
            with st.spinner("جاري إنشاء الأسئلة..."):
                res = model.generate_content(f"أنشئ 3 أسئلة اختيار من متعدد من هذا النص: {st.session_state.context[:10000]}")
                st.write(res.text)

# 5. منطقة الدردشة
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("اسأل المنهج..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        if st.session_state.context:
            full_prompt = f"أجب من النص فقط: {st.session_state.context[:15000]}\nالسؤال: {prompt}"
            try:
                response = model.generate_content(full_prompt)
                st.write(response.text)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error("حدث خطأ في جلب الرد، تأكد من صلاحية مفتاح الـ API.")
        else:
            st.warning("يرجى رفع ملف أولاً.")
