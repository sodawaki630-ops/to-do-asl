import streamlit as st

# ------------------- CONFIG -------------------
st.set_page_config(page_title="To-Do App", page_icon="📝", layout="centered")

# ------------------- CUSTOM UI STYLE -------------------
st.markdown("""
<style>
.main {
    background-color: #f2f4f8;
}

.todo-card {
    background: white;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0px 5px 20px rgba(0,0,0,0.1);
    width: 420px;
    margin: auto;
}

.task-box {
    background: #e7f0ff;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 8px;
}

input, textarea {
    border-radius: 8px !important;
}

</style>
""", unsafe_allow_html=True)

# ------------------- SESSION STATE -------------------
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# ------------------- UI -------------------
st.markdown("<div class='todo-card'>", unsafe_allow_html=True)

st.markdown("## 📝 To-Do List")

new_task = st.text_input("เพิ่มงานใหม่:")

if st.button("เพิ่มงาน"):
    if new_task.strip():
        st.session_state.tasks.append({"text": new_task, "done": False})
        st.rerun()

# ------------------- SHOW TASKS -------------------
for i, task in enumerate(st.session_state.tasks):
    col1, col2 = st.columns([0.15, 0.85])
    with col1:
        done = st.checkbox("", value=task["done"], key=f"task_{i}")
        st.session_state.tasks[i]["done"] = done
    with col2:
        if task["done"]:
            st.markdown(
                f"<div class='task-box'>✔️ <s>{task['text']}</s></div>",
                unsafe_allow_html=True)
        else:
            st.markdown(
                f"<div class='task-box'>{task['text']}</div>",
                unsafe_allow_html=True)

# ------------------- CLEAR COMPLETED -------------------
if st.button("ลบงานที่ทำเสร็จแล้ว"):
    st.session_state.tasks = [t for t in st.session_state.tasks if not t["done"]]
    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)
