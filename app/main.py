from fastapi import Depends, FastAPI
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from .dependencies import get_query_token, get_token_header
from .internal import admin
from .routers import items, users

# dependencies=[Depends(get_query_token)]
app = FastAPI()

load_dotenv()

mongo_uri = os.environ.get('MONGO_URI')

# Check if mongo_uri is set
if not mongo_uri:
    logger.error("MONGO_URI environment variable is not set.")
    raise ValueError("MONGO_URI environment variable is required.")

# Create a new client and connect to the server
client = MongoClient(mongo_uri, server_api=ServerApi('1'))
database = client["virtual_nutritionist"]
collection = database["preferences"]

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    logger.info("Pinged your deployment. You successfully connected to MongoDB!")
    
    # Check if the document already exists before inserting
    if collection.count_documents({'goal': 100}) == 0:
        result = collection.insert_one({'goal': 100})
        logger.info("Inserted initial document with goal: 100")
except Exception as e:
    logger.error("Error connecting to MongoDB: %s", e)

app.include_router(users.router)
app.include_router(items.router)
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_token_header)],
    responses={418: {"description": "I'm a teapot"}},
)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}