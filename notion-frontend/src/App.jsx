import { useState, useEffect } from "react";
import "./App.css";

function App() {
    const [showOptions, setShowOptions] = useState(false);
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(false);

    const API_BASE_URL = "http://127.0.0.1:8000"; // Adjust if necessary

    // Fetch tasks (GET request)
    const fetchTasks = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/tasks`);
            if (!response.ok) throw new Error("Failed to fetch tasks");
            const data = await response.json();
            
            if (data && Array.isArray(data.task)) {
                setTasks(data.tasks);
            } else if (data && Array.isArray(data.tasks)) {
                setTasks(data.tasks); // API returns tasks inside an object
            } else {
                console.error("Unexpected API response:", data);
                setTasks([]);
            }
        } catch (error) {
            console.error("Error fetching tasks:", error);
            setTasks([]); // Ensure it's always an array
        } finally {
            setLoading(false);
        }
    };

    // Create a new task (POST request)
    const createTask = async () => {
        const newTask = { title: "New Task", description: "Task description" };
        try {
            const response = await fetch(`${API_BASE_URL}/tasks`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(newTask),
            });
            if (!response.ok) throw new Error("Failed to create task");
            await fetchTasks(); // Refresh tasks after adding
        } catch (error) {
            console.error(error);
        }
    };

    // Delete a task (DELETE request)
    const deleteTask = async (taskId) => {
        try {
            const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
                method: "DELETE",
            });
            if (!response.ok) throw new Error("Failed to delete task");
            await fetchTasks(); // Refresh tasks after deletion
        } catch (error) {
            console.error(error);
        }
    };

    // Update a task (PATCH request)
    const updateTask = async (taskId) => {
        const updatedData = { title: "Updated Task Title" };
        try {
            const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(updatedData),
            });
            if (!response.ok) throw new Error("Failed to update task");
            await fetchTasks(); // Refresh tasks after update
        } catch (error) {
            console.error(error);
        }
    };

    // Fetch tasks when the component loads
    useEffect(() => {
        fetchTasks();
    }, []);

    return (
        <div className="container">
            <h1>Notion Task Manager API</h1>
            <button className="toggle-btn" onClick={() => setShowOptions(!showOptions)}>
                {showOptions ? "Close Menu" : "Open Menu"}
            </button>

            {showOptions && (
                <ul className="dropdown">
                    <li onClick={fetchTasks}>GET Tasks</li>
                    <li onClick={createTask}>POST Task</li>
                    <li onClick={() => deleteTask(1)}>DELETE Task</li>
                    <li onClick={() => updateTask(1)}>PATCH Task</li>
                </ul>
            )}

            {loading && <p>Loading tasks...</p>}

            <ul>
            {Array.isArray(tasks) && tasks.length > 0 ? (
            tasks.map((task) => (
            <li key={task.id}>
            {task.title} - {task.description}
        </li>
    ))
) : (
    <p>No tasks found.</p>
)}

            </ul>
        </div>
    );
}

export default App;
