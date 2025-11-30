import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";

// Component งานแต่ละชิ้น
function TodoItem({ title, subject, deadline, progress }) {
  return (
    <div className="bg-gray-800 p-4 rounded-xl shadow-md hover:bg-gray-700 transition duration-200">
      <h2 className="text-lg font-semibold text-white">{title}</h2>
      <p className="text-gray-400 text-sm">{subject}</p>
      <p className={`mt-2 font-medium ${deadline.isSoon ? "text-red-400" : "text-gray-300"}`}>
        เดดไลน์: {deadline.text}
      </p>
      <div className="mt-3 w-full bg-gray-600 h-2 rounded-full">
        <div className="bg-green-500 h-2 rounded-full" style={{ width: `${progress}%` }} />
      </div>
      <p className="text-gray-300 text-sm mt-1">{progress}% เสร็จแล้ว</p>
    </div>
  );
}

// หน้า To-Do
function App() {
  const tasks = [
    {
      title: "แบบฝึกหัดบทที่ 3",
      subject: "คณิตศาสตร์",
      deadline: { text: "พรุ่งนี้ 17:00", isSoon: true },
      progress: 20,
    },
    {
      title: "เขียนบทความสั้น",
      subject: "ภาษาอังกฤษ",
      deadline: { text: "อีก 2 วัน", isSoon: false },
      progress: 0,
    },
  ];

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <h1 className="text-2xl font-bold text-white mb-6">📋 รายการงาน</h1>

      <div className="space-y-4">
        {tasks.map((task, i) => <TodoItem key={i} {...task} />)}
      </div>

      <button className="fixed bottom-6 right-6 bg-blue-600 text-white text-3xl w-14 h-14 rounded-full shadow-lg hover:bg-blue-500">+</button>
    </div>
  );
}

// Render
ReactDOM.createRoot(document.getElementById("root")).render(<App />);
