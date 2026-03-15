import React, { useState } from "react";
import "./App.css";

function App() {

  const [tasks, setTasks] = useState([]);
  const [input, setInput] = useState("");

  const addTask = () => {
    if (!input.trim()) return;

    setTasks([
      ...tasks,
      { id: Date.now(), text: input, completed: false }
    ]);

    setInput("");
  };

  const toggleTask = (id) => {
    setTasks(
      tasks.map(task =>
        task.id === id
          ? { ...task, completed: !task.completed }
          : task
      )
    );
  };

  const deleteTask = (id) => {
    setTasks(tasks.filter(task => task.id !== id));
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
        />

        <button onClick={addTask}>+</button>
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

            <button
              className="delete"
              onClick={() => deleteTask(task.id)}
            >
              ✕
            </button>

          </div>
        ))}
      </div>

    </div>
  );
}

export default App;