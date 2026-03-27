import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# --- إعدادات الواجهة ---
st.set_page_config(page_title="Notebook-KSIT AI", layout="wide")

# تصميم بسيط ولون فاتح
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .stButton>button { border-radius: 20px; background-color: #f0f2f6; color: #1f77b4; border: 1px solid #1f77b4; }
    .stButton>button:hover { background-color: #1f77b4; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- إعداد Gemini API ---
# استبدل 'AIzaSyDI0Xp7rX7JLD8W73b32ooWxOzeq3jrn3o' بمفتاحك الخاص
API_KEY = "AIzaSyDI0Xp7rX7JLD8W73b32ooWxOzeq3jrn3o" 
genai.configure(api_key=API_KEY)
model=genai.GenerativeModel('gemini-1.5-flash')

# --- دالة استخراج النص من الملفات ---
def extract_text(files):
    combined_text = ""
    for file in files:
        if file.type == "application/pdf":
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                combined_text += page.extract_text()
        else:
            combined_text += file.read().decode("utf-8")
    return combined_text

# --- هيكل التطبيق ---
st.title("🖥️ مساعد طلاب معهد الشيخ خليفة")
st.caption("قسم تقنيات الحاسوب | نظام التعلم الذكي المعتمد على الملفات")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "context" not in st.session_state:
    st.session_state.context = ""

# القائمة الجانبية
with st.sidebar:
    st.header("📂 لوحة التحكم")
    uploaded_files = st.file_uploader("ارفع ملفات المنهج", accept_multiple_files=True, type=['pdf', 'txt'])
    
    if uploaded_files:
        with st.spinner("جاري قراءة الملفات..."):
            st.session_state.context = extract_text(uploaded_files)
        st.success("تم تحميل المنهج بنجاح!")
    
    st.divider()
    
    # أزرار الوظائف الخاصة
    if st.button("📝 تلخيص المنهج المرفوع"):
        if st.session_state.context:
            prompt = f"قم بعمل ملخص احترافي ومنظم للمحتوى التالي لطلاب تقنيات الحاسوب: {st.session_state.context[:10000]}"
            response = model.generate_content(prompt)
            st.info(response.text)
        else:
            st.error("الرجاء رفع ملفات أولاً")

    if st.button("❓ توليد كويز (سؤال وجواب)"):
        if st.session_state.context:
            prompt = f"بناءً على هذا المحتوى، استخرج 5 أسئلة اختيار من متعدد مع الحل لشرحها للطالب: {st.session_state.context[:10000]}"
            response = model.generate_content(prompt)
            st.write(response.text)
        else:
            st.error("الرجاء رفع ملفات أولاً")

# --- منطقة الدردشة ---
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("اسأل عن أي شيء في الملفات..."):
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        if st.session_state.context:
            # تقييد الرد بالملفات فقط (RAG Logic)
            full_prompt = f"""
            أنت مساعد تعليمي لطلاب تقنيات الحاسوب بمعهد الشيخ خليفة.
            أجب على السؤال التالي بناءً على المعلومات المتوفرة في النص المرفق فقط. 
            إذا لم تجد الإجابة، قل بكل أدب أن المعلومة غير موجودة في المنهج المرفوع.
            
            النص المرفق: {st.session_state.context[:15000]}
            السؤال: {user_input}
            """
            response = model.generate_content(full_prompt)
            st.markdown(response.text)
            st.session_state.chat_history.append({"role": "assistant", "content": response.text})
        else:
            st.warning("يرجى رفع ملفات المنهج في القائمة الجانبية للبدء.")
