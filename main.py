import requests
from FastAPI import FastAPI, HTTPException

"""
    loading api key
"""
from dotenv import load_dotenv
import os

load_dotenv()
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID= od.getenv("NOTION_DATABASE_ID")

#checking for update