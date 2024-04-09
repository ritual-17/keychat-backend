from bson import ObjectId
from controllers.chat_controller import ChatController
from database.db import get_contacts_collection, get_chat_collection

class ContactsController:
    def __init__(self):
        self.contacts_collection = get_contacts_collection()

    def add_contact(self, user_id, contact_user_id):
        contact_data = {
            "userId": ObjectId(user_id),
            "contacts": [{"contactUserId": ObjectId(contact_user_id)}]
        }
        chat_data = {
            "participants": [ObjectId(user_id), ObjectId(contact_user_id)],
            "subject": "subject",
            "createdAt": "unknown",
            "messages": []
        }
        get_chat_collection().insert_one(chat_data)
        return self.contacts_collection.insert_one(contact_data).inserted_id

    def get_contacts(self, user_id):
        return self.contacts_collection.find_one({"userId": ObjectId(user_id)})

    def add_contact_to_list(self, user_id, contact_user_id):
        contacts = self.contacts_collection.find({"userId": ObjectId(user_id)})
        if not contacts:
          return self.add_contact(user_id, contact_user_id)
        chat_data = {
            "participants": [ObjectId(user_id), ObjectId(contact_user_id)],
            "subject": "subject",
            "createdAt": "unknown",
            "messages": []
        }
        get_chat_collection().insert_one(chat_data)
        return self.contacts_collection.update_one(
            {"userId": ObjectId(user_id)},
            {"$addToSet": {"contacts": {"contactUserId": ObjectId(contact_user_id)}}}
        )

    def remove_contact_from_list(self, user_id, contact_user_id):
        return self.contacts_collection.update_one(
            {"userId": ObjectId(user_id)},
            {"$pull": {"contacts": {"contactUserId": ObjectId(contact_user_id)}}}
        )
