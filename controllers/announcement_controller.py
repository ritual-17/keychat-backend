from bson import ObjectId
from datetime import datetime
from database.db import get_announcements_collection

class AnnouncementController:
    def __init__(self):
        self.announcements_collection = get_announcements_collection()

    def create_announcement(self, title, content, created_by):
        announcement_data = {
            "title": title,
            "content": content,
            "createdAt": datetime.now(),
            "createdBy": ObjectId(created_by)
        }
        return self.announcements_collection.insert_one(announcement_data).inserted_id

    def get_announcement(self, announcement_id):
        return self.announcements_collection.find_one({"_id": ObjectId(announcement_id)})

    def get_all_announcements(self):
        return list(self.announcements_collection.find({}))
