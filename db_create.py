from datetime import datetime
import pymongo
from bson import ObjectId
from pymongo import MongoClient

# Connect to MongoDB
client=MongoClient('localhost',27017)

# Create/access the database
db = client['secure_chat_app']

# Define collections
users_collection=db['users']
contacts_collection=db['contacts']
chats_collection=db['chats']
files_collection=db['files']
announcements_collection=db['announcements']
notifications_collection =db['notifications']



# Close MongoDB connection
client.close()
