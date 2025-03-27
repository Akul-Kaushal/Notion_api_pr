import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000"; // Change this to your FastAPI URL

// Fetch tasks from the backend
export const getTasks = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/tasks`);
        return response.data;
    } catch (error) {
        console.error("Error fetching tasks:", error);
        throw error;
    }
};

// Add a new task
export const addTask = async (taskData) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/tasks`, taskData);
        return response.data;
    } catch (error) {
        console.error("Error adding task:", error);
        throw error;
    }
};

// Update a task
export const updateTask = async (taskId, updatedData) => {
    try {
        const response = await axios.patch(`${API_BASE_URL}/tasks/${taskId}`, updatedData);
        return response.data;
    } catch (error) {
        console.error("Error updating task:", error);
        throw error;
    }
};

// Delete a task
export const deleteTask = async (taskId) => {
    try {
        await axios.delete(`${API_BASE_URL}/tasks/${taskId}`);
    } catch (error) {
        console.error("Error deleting task:", error);
        throw error;
    }
};
