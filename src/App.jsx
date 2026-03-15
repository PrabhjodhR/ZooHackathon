import React, { useState } from "react";
import "./App.css";

function App() {
  const [tasks, setTasks] = useState([]);
  const [input, setInput] = useState("");
  const [organized, setOrganized] = useState(null);
  const [loading, setLoading] = useState(false);

  const addTask = () => {
    if (!input.trim()) return;
    setTasks([...tasks, { id: Date.now(), text: input, completed: false }]);
    setInput("");
  };

  const toggleTask = (id) => {
    setTasks(tasks.map(task =>
      task.id === id ? { ...task, completed: !task.completed } : task
    ));
  };

  const deleteTask = (id) => {
    setTasks(tasks.filter(task => task.id !== id));
  };

  const organizeTasks = async () => {
    if (tasks.length === 0) return;
    const brainDump = tasks.map(task => task.text).join("\n");
    setLoading(true);
    try {
      const res = await fetch("http://localhost:5000/organize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ brainDump }),
      });
      const data = await res.json();
      setOrganized(data);
    } catch (err) {
      console.error("Error organizing tasks:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Brain Dump</h1>
      <p className="subtitle">What's on your mind?</p>

      <div className="inputBox">
        <textarea
          placeholder="Dump everything here..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && (e.preventDefault(), addTask())}
        />
        <div className="buttons">
          <button onClick={addTask}>+</button>
          <button onClick={organizeTasks}>
            {loading ? "Thinking..." : "Organize Tasks"}
          </button>
        </div>
      </div>

      <div className="taskList">
        {tasks.map(task => (
          <div className="task" key={task.id}>
            <input
              type="checkbox"
              checked={task.completed}
              onChange={() => toggleTask(task.id)}
            />
            <span className={task.completed ? "completed" : ""}>
              {task.text}
            </span>
            <button className="delete" onClick={() => deleteTask(task.id)}>✕</button>
          </div>
        ))}
      </div>

      {organized && (
        <div className="organized">
          <h2>Organized Tasks</h2>
          <p><strong>Day load:</strong> {organized.day_load}</p>
          <p><strong>Reasoning:</strong> {organized.reasoning}</p>
          <ul>
            <li><strong>Must do today:</strong> {organized.must_do_today?.join(", ")}</li>
            <li><strong>Should do today:</strong> {organized.should_do_today?.join(", ")}</li>
            <li><strong>Quick wins:</strong> {organized.quick_wins?.join(", ")}</li>
            <li><strong>Can wait:</strong> {organized.can_wait?.join(", ")}</li>
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
