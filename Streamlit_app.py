import streamlit as st
import json
from datetime import datetime as dt, date

# -------------------- Config --------------------
st.set_page_config(page_title="Ultimate To-Do App", page_icon="📝", layout="wide")

# -------------------- CSS --------------------
st.markdown("""
<style>
body {
    background: linear-gradient(120deg, #f6f9fc, #eef2f3);
    font-family: 'Segoe UI';
}

/* Task Card */
.task-card {
    background: white;
    padding: 18px;
    border-radius: 15px;
    margin-bottom: 15px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    transition: 0.3s;
}
.task-card:hover {
    box-shadow: 0 6px 18px rgba(0,0,0,0.15);
}

/* Animation: Slide-in + Fade */
.task-card.new {
    animation: slideFade 0.7s ease-out;
}
@keyframes slideFade {
    0% {opacity: 0; transform: translateX(50px);}
    100% {opacity: 1; transform: translateX(0);}
}

/* Deadline text */
.deadline-text {
    color: #ff4b4b;
    font-weight: 600;
}

/* Progress bar */
.progress-bar {
    height: 10px;
    border-radius: 10px;
    background: #e5e5e5;
}
.progress-fill {
    height: 10px;
    border-radius: 10px;
    background: #4CAF50;
}

/* Popup Notification */
.popup {
    position: fixed;
    top: 20px;
    right: 20px;
    background: #4CAF50;
    color: white;
    padding: 15px 25px;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    opacity: 0;
    transform: translateY(-20px);
    animation: popupShow 0.5s forwards, popupFadeOut 0.5s 2.5s forwards;
    z-index:999;
}
@keyframes popupShow {
    from {opacity: 0; transform: translateY(-20px);}
    to {opacity: 1; transform: translateY(0);}
}
@keyframes popupFadeOut {
    from {opacity:1;}
    to {opacity:0; transform: translateY(-20px);}
}
button:hover {
    transform: scale(1.1);
    transition: transform 0.2s;
}
</style>
""", unsafe_allow_html=True)

# -------------------- Session State --------------------
if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "sound_played" not in st.session_state:
    st.session_state.sound_played = set()  # เก็บงานที่เล่นเสียงแล้ว

# -------------------- Title --------------------
st.title("📝 Ultimate Animated To-Do App")

# -------------------- Add Task --------------------
st.subheader("➕ เพิ่มงานใหม่")
col1, col2, col3 = st.columns([4,3,3])
with col1:
    task_name = st.text_input("ชื่องาน")
with col2:
    deadline = st.date_input("เดดไลน์", value=date.today())
with col3:
    category = st.text_input("หมวดหมู่")
progress = st.slider("ความคืบหน้า (%)", 0, 100, 0)

if st.button("เพิ่มงาน"):
    st.session_state.tasks.append({
        "name": task_name,
        "deadline": str(deadline),
        "progress": progress,
        "category": category.strip(),
        "completed": False,
        "new": True
    })
    st.markdown("<div class='popup'>เพิ่มงานสำเร็จ! 🎉</div>", unsafe_allow_html=True)

# -------------------- Filter --------------------
st.subheader("🔎 กรองงาน")
filter_category = st.text_input("กรองตามหมวดหมู่ (Category)")

# -------------------- Progress Summary --------------------
total = len(st.session_state.tasks)
done = sum(1 for t in st.session_state.tasks if t["completed"])
if total > 0:
    st.progress(done / total)
    st.write(f"✔ งานเสร็จแล้ว {done}/{total} งาน")
else:
    st.write("ยังไม่มีงาน")

# -------------------- Show Tasks --------------------
st.subheader("📌 รายการงาน")
today = dt.now().date()
for i, task in enumerate(st.session_state.tasks):
    # Filter by category
    if filter_category and task["category"] != filter_category:
        continue

    deadline_date = dt.strptime(task["deadline"], "%Y-%m-%d").date()
    remaining_days = (deadline_date - today).days

    card_class = "task-card new" if task.get("new") else "task-card"
    st.markdown(f"<div class='{card_class}'>", unsafe_allow_html=True)

    colA, colB = st.columns([6,1])
    with colA:
        st.markdown(f"### {task['name']}")
        st.markdown(f"🗓 เดดไลน์: <span class='deadline-text'>{task['deadline']}</span>", unsafe_allow_html=True)
        if task["category"]:
            st.markdown(f"📂 หมวดหมู่: {task['category']}")
        st.markdown("ความคืบหน้า:")
        st.markdown(
            f"""
            <div class="progress-bar">
                <div class="progress-fill" style="width:{task['progress']}%"></div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # แจ้งเตือนเสียงถ้าใกล้เดดไลน์ และเล่นแค่ครั้งเดียว
        if remaining_days <= 1 and not task["completed"] and task["name"] not in st.session_state.sound_played:
            st.audio("https://upload.wikimedia.org/wikipedia/commons/c/cf/Alert-tone.mp3")
            st.warning(f"⏰ งานนี้ใกล้ถึงเดดไลน์แล้ว!")
            st.session_state.sound_played.add(task["name"])

    with colB:
        # ปุ่ม ✔ หน้า / 🗑 หลัง
        if st.button("✔", key=f"done{i}"):
            task["completed"] = True
            st.success("งานเสร็จแล้ว!")
        st.write(" ")  # เว้นระยะ
        if st.button("🗑", key=f"delete{i}"):
            st.session_state.tasks.pop(i)
            st.rerun()

    task["new"] = False
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------- Calendar --------------------
st.subheader("📅 ปฏิทินงาน")
calendar_date = st.date_input("เลือกวันที่เพื่อดูงานของวันนั้น", value=today)
day_tasks = [t for t in st.session_state.tasks if t["deadline"] == str(calendar_date)]
if day_tasks:
    st.write("งานของวันนั้น:")
    for t in day_tasks:
        st.write(f"- {t['name']} (หมวดหมู่: {t['category']}, ความคืบหน้า: {t['progress']}%)")
else:
    st.info("ไม่มีงานในวันนี้")

# -------------------- Share Tasks --------------------
st.subheader("📤 แชร์งานให้เพื่อน")
export_data = json.dumps(st.session_state.tasks)
st.code(export_data, language="json")
st.info("เพื่อนนำ JSON นี้ไปวางในแอปเพื่อโหลดงานเข้าไปได้เลย")
