import requests
from fastapi import FastAPI, HTTPException  
import json
from dotenv import load_dotenv
import os
from notion_client import Client  

"""
    Setting up Notion Client
"""


load_dotenv()
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")  


notion = Client(auth=NOTION_API_KEY) 
database_id = NOTION_DATABASE_ID

# Fetching Database entry / drop
try:
    response = notion.databases.query(database_id=database_id)
    print(json.dumps(response, indent=4))
except Exception as e:
    print("Error:", e)
