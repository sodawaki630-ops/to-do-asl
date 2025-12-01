import streamlit as st

st.set_page_config(page_title="To-Do App + Floating Button", layout="wide")

# ---------------- CSS Floating Button ----------------
st.markdown("""
<style>
/* Floating Add Button */
.floating-btn {
    position: fixed;
    bottom: 30px;
    right: 30px;
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, #4facfe, #00f2fe);
    color: white;
    border-radius: 50%;
    border: none;
    font-size: 32px;
    text-align: center;
    line-height: 60px;
    cursor: pointer;
    box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    transition: transform 0.2s;
    z-index: 999;
}

.floating-btn:hover {
    transform: scale(1.1);
}
</style>
""", unsafe_allow_html=True)

# ---------------- Button + Popup ----------------
# เราจะใช้ st.markdown แทน button ปกติ
st.markdown("""
<button class="floating-btn" onclick="document.getElementById('input-section').scrollIntoView({behavior: 'smooth'});">+</button>
""", unsafe_allow_html=True)

# ---------------- Input Section ----------------
st.markdown("<div id='input-section'></div>", unsafe_allow_html=True)
st.subheader("เพิ่มงานใหม่")
task_name = st.text_input("ชื่องาน")
if st.button("เพิ่มงาน"):
    st.success(f"เพิ่มงาน: {task_name}")
