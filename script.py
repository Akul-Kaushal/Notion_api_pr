from dotenv import load_dotenv
import requests
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Load environment variables
load_dotenv()
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

def get_notion_version():
    return os.getenv("NOTION_VERSION", "2022-06-28")

# FastAPI Setup
app = FastAPI()

# Allow requests from your frontend (Vite)
origins = [
    "http://localhost:5173",  # Vite frontend
    "http://127.0.0.1:5173"   # Alternative localhost address
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specific frontend origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": get_notion_version(),
    "Content-Type": "application/json"
}

@app.get("/")
def root():
    return {"message": "Notion Task Manager is Running"}

# 1. **POST** - Create a Task
class TaskRequest(BaseModel):
    task_name: str
    due_date: Optional[str] = None
    priority: Optional[str] = None

@app.post("/tasks")
def create_task(task: TaskRequest):
    url = "https://api.notion.com/v1/pages"

    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": task.task_name}}]}
        }
    }

    if task.due_date:
        data["properties"]["Due Date"] = {"date": {"start": task.due_date}}

    if task.priority:
        data["properties"]["Priority"] = {"select": {"name": task.priority}}

    response = requests.post(url, headers=headers, json=data)
    
    try:
        response.raise_for_status()
        return {"message": "Task created successfully", "notion_response": response.json()}
    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=response.status_code, detail=str(e))

# 2. **GET** - Fetch All Tasks (Formatted)
@app.get("/tasks")
def get_tasks():
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"

    response = requests.post(url, headers=headers)

    try:
        response.raise_for_status()
        data = response.json()

        tasks = []
        for item in data["results"]:
            properties = item["properties"]
            task = {
                "id": item["id"],
                "name": properties["Name"]["title"][0]["text"]["content"] if properties["Name"]["title"] else "Unnamed Task",
                "due_date": properties.get("Due Date", {}).get("date", {}).get("start", None),
                "priority": properties.get("Priority", {}).get("select", {}).get("name", None),
            }
            tasks.append(task)

        return {"tasks": tasks}
    
    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=response.status_code, detail=str(e))

# 3. **PATCH** - Update Task Properties
class TaskUpdate(BaseModel):
    task_name: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None

@app.patch("/tasks/{task_id}")
def update_task(task_id: str, task: TaskUpdate):
    url = f"https://api.notion.com/v1/pages/{task_id}"
    data = {"properties": {}}

    if task.task_name:
        data["properties"]["Name"] = {"title": [{"text": {"content": task.task_name}}]}

    if task.due_date:
        data["properties"]["Due Date"] = {"date": {"start": task.due_date}}

    if task.priority:
        data["properties"]["Priority"] = {"select": {"name": task.priority}}

    response = requests.patch(url, headers=headers, json=data)
    
    try:
        response.raise_for_status()
        return {"message": "Task updated successfully"}
    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=response.status_code, detail=str(e))

# 4. **DELETE** - Delete Task 
@app.delete("/tasks/{task_id}")
def delete_task(task_id: str):
    url = f"https://api.notion.com/v1/pages/{task_id}"  # Corrected URL

    response = requests.delete(url, headers=headers)

    try:
        response.raise_for_status()
        return {"message": "Task deleted successfully"}
    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=response.status_code, detail=str(e))


# # 3.5 PUT
# class TaskUpdate(BaseModel):
#     task_name: str
#     due_date: str
#     priority: str

# @app.put("/tasks/{task_id}")
# async def update_task(task_id: str, task: TaskUpdate):
#     url = f"https://api.notion.com/v1/pages/{task_id}"

#     data = {
#         "properties": {
#             "Name": {"title": [{"text": {"content": task.task_name}}]},
#             "Due Date": {"date": {"start": task.due_date}},
#             "Priority": {"select": {"name": task.priority}}  
#         }
#     }

#     response = requests.patch(url, headers=headers, json=data)

#     if response.status_code != 200:
#         raise HTTPException(status_code=response.status_code, detail=response.json())

#     return {"message": "Task updated successfully"}

# 4. Delete
@app.delete("/tasks/{task_id}")
def delete_task(task_id: str):
    url = f"https://api.notion.com/v1/blocks/{task_id}"

    response = requests.delete(url, headers=headers)

    if response.status_code == 200:
        return {"message": "Task deleted successfully"}
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to delete task")
