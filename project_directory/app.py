import streamlit as st

# كود طلب كلمة السر في البداية
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    pwd = st.text_input("🔒 أدخل كلمة السر", type="password")
    if pwd == "1234":
        st.session_state.authenticated = True
    elif pwd != "":
        st.error("كلمة السر غير صحيحة")

if not st.session_state.authenticated:
    check_password()
    st.stop()

# إذا كلمة السر صحيحة نكمل هنا عرض الصفحة

st.markdown(
    """
    <div dir="rtl" style="text-align: right; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
        <h1>🏗️ تطبيق توثيق مشروع بناء عمارة</h1>
        <p><strong>إعداد: أنس الراجح</strong></p>
        <p>مرحبًا بك في تطبيق Streamlit المصمم لتوثيق وحساب تكاليف مشروع بناء عمارة.</p>
        <p>🔹 يمكنك من خلال هذا التطبيق:</p>
        <ul>
            <li>تسجيل المهام وتكاليفها.</li>
            <li>توثيق المراحل بصور وتوصيفات.</li>
            <li>إضافة فواتير وحساب المبلغ المتبقي.</li>
        </ul>
        <p>🧾 استخدم القائمة الجانبية للتنقل بين الصفحات.</p>
    </div>
    """, 
    unsafe_allow_html=True
)
