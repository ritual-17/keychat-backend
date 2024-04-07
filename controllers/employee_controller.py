from bson import ObjectId
from database.db import get_employee_collection, db


class Employee:
    def __init__(self, employee_data):
        self.employee_data = employee_data

    def add_to_db(self):
        employee_collection = get_employee_collection()
        return employee_collection.insert_one(self.employee_data).inserted_id

    @staticmethod
    def get_all():
        employee_collection = get_employee_collection()
        return list(employee_collection.find({}))

    @staticmethod
    def get(employee_id):
        employee_collection = get_employee_collection()
        return employee_collection.find_one({'_id': ObjectId(employee_id)})

    @staticmethod
    def update(employee_id, update_data):
        employee_collection = get_employee_collection()
        return employee_collection.update_one({'_id': ObjectId(employee_id)}, {'$set': update_data})

    @staticmethod
    def delete(employee_id):
        employee_collection = get_employee_collection()
        return employee_collection.delete_one({'_id': ObjectId(employee_id)})
    


    
    