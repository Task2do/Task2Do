from datetime import datetime
import uvicorn as uvicorn
from pymongo import MongoClient

from fastapi import FastAPI, HTTPException, status, Query, Response
from pydantic import BaseModel
from typing import Optional
from random import randrange
import os
from dotenv import load_dotenv

load_dotenv()
connection_string = os.getenv('MONGO_CONNECTION')
print(connection_string)
# app = FastAPI()
client = MongoClient(connection_string)
mydb = client["Task2Do"]
collection=mydb["users"]
x = collection.insert_one({"name":"shira"})
print(client)