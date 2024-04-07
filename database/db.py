
import os
from pymongo import MongoClient
from pymongo.collection import Collection


# Environment setup
db_env = os.getenv('DB_ENV', 'prod')  # Default to 'prod' if not set

# Local database connection
if db_env == 'local':
    client = MongoClient('localhost', 27017)
    db = client['3A04']
else:
    # Production database connection
    connection_url = "mongodb+srv://Generic:37arE0j7XLKMKzJC@3a04.mnc8dzm.mongodb.net/?retryWrites=true&ssl=true&tlsCAFile=./isrgrootx1.pem"
    client = MongoClient(connection_url)
    db = client['3A04']

# Functions to get collections (if needed elsewhere in your application)
def get_collection(collection_name):
    return db[collection_name]

def get_employee_collection() -> Collection:
    return db["Employees"]

def get_contacts_collection() -> Collection:
    return db["Contacts"]

def get_chat_collection() -> Collection:
    return db["Chats"]

def get_announcements_collection() -> Collection:
    return db["Announcements"]

def get_notifications_collection() -> Collection:
    return db["Notifications"]

