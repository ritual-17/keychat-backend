from bson import ObjectId
from datetime import datetime
from database.db import get_chat_collection
import json
import KDC

# Define user_secrets dictionary
usernames = {
  "alice": "password12345678",
  "bob" : "password87654321",
  "cody": "passwordabcdefghi"
}

user_secrets = {
  "alice": usernames['alice'].encode(),
  "bob" : usernames['bob'].encode(),
  "cody": usernames['cody'].encode()
}
class ChatController:
    def __init__(self, kdc):
        self.chat_collection = get_chat_collection()
        self.kdc = kdc  # Initialize KDC instance

    def create_chat(self, participants, subject):
        chat_data = {
            "participants": [ObjectId(participant) for participant in participants],
            "subject": subject,
            "createdAt": datetime.now(),
            "messages": []
        }
        chat_id = self.chat_collection.insert_one(chat_data).inserted_id
        return self.kdc.encrypt_shared_key(str(chat_id), participants)  # Encrypt the chat ID before returning

    def add_message(self, chat_id, sender_id, content):
        message_data = {
            "messageId": str(ObjectId()),
            "senderId": ObjectId(sender_id),
            "content": content,
            "sentAt": datetime.now().isoformat(),
            "status": "sent"
        }
        self.chat_collection.update_one(
            {"_id": ObjectId(chat_id)},
            {"$push": {"messages": message_data}}
        )

    def get_chat(self, chat_id):
        chat = self.chat_collection.find_one({"_id": ObjectId(chat_id)})
        if chat:
            chat['_id'] = str(chat['_id'])  # Convert ObjectId to string
            chat['participants'] = [str(participant) for participant in chat['participants']]
            chat['createdAt'] = chat['createdAt'].isoformat() if 'createdAt' in chat else 'Unknown'
            chat_data = json.dumps(chat)  # Convert chat data to JSON format before encryption
            return self.kdc.encrypt_shared_key(chat_data, chat['participants'])  # Encrypt chat data
        else:
            return None

    def update_message_status(self, chat_id, message_id, status):
        self.chat_collection.update_one(
            {"_id": ObjectId(chat_id), "messages.messageId": ObjectId(message_id)},
            {"$set": {"messages.$.status": status}}
        )