import streamlit as st
import json
from datetime import datetime as dt, date

# -------------------- Config --------------------
st.set_page_config(page_title="Ultimate To-Do App with Subtasks", page_icon="📝", layout="wide")

# -------------------- CSS --------------------
st.markdown("""
<style>
body {
    background: linear-gradient(120deg, #f6f9fc, #eef2f3);
    font-family: 'Segoe UI';
}

/* Task Card */
.task-card {
    padding: 18px;
    border-radius: 15px;
    margin-bottom: 15px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    transition: 0.3s;
}
.task-card:hover {
    box-shadow: 0 6px 18px rgba(0,0,0,0.15);
}

/* Priority Colors */
.priority-high {background-color:#ff4b4b; color:white;}
.priority-medium {background-color:white; color:black;}
.priority-low {background-color:#111; color:white;}

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
    st.session_state.sound_played = set()

# -------------------- Title --------------------
st.title("📝 Ultimate To-Do App with Subtasks")

# -------------------- Add Task --------------------
st.subheader("➕ เพิ่มงานใหม่")
col1, col2, col3, col4 = st.columns([3,3,3,3])
with col1:
    task_name = st.text_input("ชื่องาน")
with col2:
    deadline = st.date_input("เดดไลน์", value=date.today())
with col3:
    category = st.text_input("หมวดหมู่")
with col4:
    priority = st.selectbox("Priority", ["High","Medium","Low"])
num_sub = st.number_input("จำนวนงานย่อย", min_value=0, max_value=10, value=0, step=1)

subtasks = []
for i in range(num_sub):
    sub_name = st.text_input(f"งานย่อย {i+1} ชื่อ", key=f"sub{i}")
    subtasks.append({"name": sub_name, "completed": False})

progress = 0  # Progress จะคำนวณจากงานย่อย

if st.button("เพิ่มงาน"):
    st.session_state.tasks.append({
        "name": task_name,
        "deadline": str(deadline),
        "category": category.strip(),
        "priority": priority,
        "subtasks": subtasks,
        "completed": False,
        "new": True
    })
    st.markdown("<div class='popup'>เพิ่มงานสำเร็จ! 🎉</div>", unsafe_allow_html=True)

# -------------------- Filter --------------------
st.subheader("🔎 กรองงาน")
filter_category = st.text_input("กรองตามหมวดหมู่ (Category)")
filter_priority = st.selectbox("กรองตาม Priority", ["All","High","Medium","Low"])

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
    # Filter
    if filter_category and task["category"] != filter_category:
        continue
    if filter_priority != "All" and task["priority"] != filter_priority:
        continue

    # คำนวณ Progress จากงานย่อย
    if task["subtasks"]:
        completed_sub = sum(1 for s in task["subtasks"] if s["completed"])
        progress = int(completed_sub / len(task["subtasks"]) * 100)
    else:
        progress = 0 if not task["completed"] else 100

    # Priority color
    if task["priority"]=="High":
        card_class = "task-card new priority-high"
    elif task["priority"]=="Medium":
        card_class = "task-card new priority-medium"
    else:
        card_class = "task-card new priority-low"

    st.markdown(f"<div class='{card_class}'>", unsafe_allow_html=True)

    colA, colB = st.columns([6,1])
    with colA:
        st.markdown(f"### {task['name']}")
        st.markdown(f"🗓 เดดไลน์: <span class='deadline-text'>{task['deadline']}</span>", unsafe_allow_html=True)
        if task["category"]:
            st.markdown(f"📂 หมวดหมู่: {task['category']}")
        st.markdown(f"🔹 Priority: {task['priority']}")
        st.markdown("ความคืบหน้า:")
        st.markdown(
            f"""
            <div class="progress-bar">
                <div class="progress-fill" style="width:{progress}%"></div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # แสดงงานย่อย
        if task["subtasks"]:
            st.markdown("**งานย่อย:**")
            for j, sub in enumerate(task["subtasks"]):
                col1, col2 = st.columns([8,2])
                with col1:
                    st.write(sub["name"])
                with col2:
                    if st.checkbox("✔", key=f"{i}_sub_{j}", value=sub["completed"]):
                        sub["completed"] = True
                    else:
                        sub["completed"] = False

        # แจ้งเตือนเสียงถ้าใกล้เดดไลน์
        deadline_date = dt.strptime(task["deadline"], "%Y-%m-%d").date()
        remaining_days = (deadline_date - today).days
        if remaining_days <= 1 and not task["completed"] and task["name"] not in st.session_state.sound_played:
            st.audio("https://upload.wikimedia.org/wikipedia/commons/c/cf/Alert-tone.mp3")
            st.warning(f"⏰ งานนี้ใกล้ถึงเดดไลน์แล้ว!")
            st.session_state.sound_played.add(task["name"])

    with colB:
        if st.button("✔", key=f"done{i}"):
            # ทำงานหลักเสร็จ = ทำงานย่อยทั้งหมดเสร็จด้วย
            for sub in task["subtasks"]:
                sub["completed"] = True
            task["completed"] = True
            st.success("งานเสร็จแล้ว!")
        st.write(" ")
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
        st.write(f"- {t['name']} (หมวดหมู่: {t['category']}, ความคืบหน้า: {progress}%)")
else:
    st.info("ไม่มีงานในวันนี้")

# -------------------- Share Tasks --------------------
st.subheader("📤 แชร์งานให้เพื่อน")
export_data = json.dumps(st.session_state.tasks, ensure_ascii=False, indent=2)
st.code(export_data, language="json")
st.info("เพื่อนนำ JSON นี้ไปวางในแอปเพื่อโหลดงานเข้าไปได้เลย")
