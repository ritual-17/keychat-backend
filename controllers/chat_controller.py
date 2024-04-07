from bson import ObjectId
from datetime import datetime
from database.db import get_chat_collection

class ChatController:
    def __init__(self):
        self.chat_collection = get_chat_collection()

    def create_chat(self, participants, subject):
        chat_data = {
            "participants": [ObjectId(participant) for participant in participants],
            "subject": subject,
            "createdAt": datetime.now(),
            "messages": []
        }
        return self.chat_collection.insert_one(chat_data).inserted_id

    def add_message(self, chat_id, sender_id, content):
        message_data = {
            "messageId": ObjectId(),
            "senderId": ObjectId(sender_id),
            "content": content,
            "sentAt": datetime.now(),
            "status": "sent"
        }
        return self.chat_collection.update_one(
            {"_id": ObjectId(chat_id)},
            {"$push": {"messages": message_data}}
        )

    def get_chat(self, chat_id):
        return self.chat_collection.find_one({"_id": ObjectId(chat_id)})

    def update_message_status(self, chat_id, message_id, status):
        return self.chat_collection.update_one(
            {"_id": ObjectId(chat_id), "messages.messageId": ObjectId(message_id)},
            {"$set": {"messages.$.status": status}}
        )
