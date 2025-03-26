from dotenv import load_dotenv
import requests
import os
from fastapi import FastAPI , HTTPException
from pydantic import BaseModel

"""
    loading env
"""
load_dotenv()
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")



def get_notion_version():
    """
    Returns the latest Notion API version.
    Update this manually when Notion releases a new version.
    """
    return os.getenv("NOTION_VERSION", "2022-06-28")  


"""
    FastAPI setup
"""

app = FastAPI()

headers = {
    "Authorization" : f"Bearer {NOTION_API_KEY}",
    "Notion-Version" : get_notion_version(),
    "Content-Type": "application/json"
}

@app.get("/")
def root():
    return {"message":"Notion Task Manager is Running"}

@app.get("/test-notion")
def test_notion():
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail="failed")

"""
    adding the following methods
    1. POST :: /tasks : add a new task to notion
    2. GET :: /tasks : fetch all tasks from notion
    3. PATCH :: /tasks{id} : Update a task status in notion
    4. DELETE :: /tasks{id} : Delete a task from notion
"""

# 1. POST
class TaskRequest(BaseModel):
    task_name: str
    due_date: str = None
    priority: str = None

@app.post("/task")
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

    if response.status_code == 200:
        return {"message": "Task created successfully", "notion_response": response.json()}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


# 2. GET
@app.get("/tasks")
def get_tasks():
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"

    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch tasks")

# 3. Patch
class TaskUpdate(BaseModel):
    task_name: str | None = None  # Optional fields for partial update
    due_date: str | None = None
    priority: str | None = None
@app.patch("/tasks/{task_id}")
async def update_task(task_id: str, task: TaskUpdate):
    url = f"https://api.notion.com/v1/pages/{task_id}"
    data = {"properties": {}}

    if task.task_name:
        data["properties"]["Name"] = {"title": [{"text": {"content": task.task_name}}]}

    if task.due_date:
        data["properties"]["Due Date"] = {"date": {"start": task.due_date}}

    if task.priority:
        data["properties"]["Priority"] = {"select": {"name": task.priority}}

    response = requests.patch(url, headers=headers, json=data)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return {"message": "Task updated successfully"}


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
