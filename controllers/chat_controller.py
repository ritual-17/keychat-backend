from bson import ObjectId
from datetime import datetime
from database.db import get_chat_collection
import json
import KDC

class ChatController:
    def __init__(self, kdc):
        self.chat_collection = get_chat_collection()
        self.kdc = kdc  # Initialize KDC instance

    def create_chat(self, participants, subject, shared_key):
        chat_data = {
            "participants": [ObjectId(participant) for participant in participants],
            "subject": subject,
            "createdAt": datetime.now(),
            "messages": []
        }
        chat_id = self.chat_collection.insert_one(chat_data).inserted_id
        return self.kdc.encrypt_shared_key(str(chat_id).encode(), shared_key)  # Encrypt the chat ID before returning

    def add_message(self, chat_id, sender_id, content):
      try:
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
        return True
      except Exception as e:
        print(f"Error adding message: {e}")
        return False

    def get_chat(self, chat_id, shared_key):
        chat = self.chat_collection.find_one({"_id": ObjectId(chat_id)})
        if chat:
            chat['_id'] = str(chat['_id'])  # Convert ObjectId to string
            chat['participants'] = [str(participant) for participant in chat['participants']]
            chat['createdAt'] = str(chat['createdAt']) if 'createdAt' in chat else 'Unknown'
            chat['messages'] = [{
                **message, 'messageId':
                str(message['messageId']),
                'senderId':
                str(message['senderId']),
                'sentAt':
                str(message['sentAt']) if 'sentAt' in message else 'Unknown',
                'status':
                message.get('status', 'Unknown')
            } for message in chat['messages']]
            chat_data = json.dumps(chat)  # Convert chat data to JSON format before encryption
            return self.kdc.encrypt_shared_key(chat_data.encode(), shared_key)  # Encrypt chat data
        else:
            return None

    def update_message_status(self, chat_id, message_id, status):
        self.chat_collection.update_one(
            {"_id": ObjectId(chat_id), "messages.messageId": ObjectId(message_id)},
            {"$set": {"messages.$.status": status}}
        )