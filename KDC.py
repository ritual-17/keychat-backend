import secrets
import json
import sys

import AES

class KDC:
    def __init__(self, user_secrets, service_secrets):
        self.user_secrets = user_secrets #users keys
        self.service_secrets = service_secrets #service keys
        self.K = secrets.token_bytes(16) #the KDC's key
        self.crypto_system = AES.AES() #our encryption algorithm

    #register the user by adding their secret key to the system
    def register(self, username, secret):
        self.user_secrets[username] = secret

    #return encrypted TGT payload, including session key and TGT encrypted using the user's secret key
    def return_TGT(self, username):
        session_key = self.generate_session_key()
        tgt = self.generate_TGT(username, session_key)

        payload = {"session_key": str(session_key), "tgt": str(tgt)}
        payload_bytes = self.get_payload_bytes(payload)

        response = self.crypto_system.encrypt(payload_bytes, self.user_secrets[username])
        return response
    
    #for when user is requesting a ticket to talk to a service
    def return_ticket(self, username, recipient, tgt):
        if recipient not in self.service_secrets:
            return None
        #generate shared key
        shared_key = self.generate_session_key()

        #decrypt tgt using KDC key to get session key of user
        tgt_decrypted = self.crypto_system.decrypt(tgt, self.K)
        tgt_decrypted_json = json.loads(tgt_decrypted)
        user_session_key = eval(tgt_decrypted_json["session_key"]) #need to use eval() to convert string to bytes
    
        #generate ticket encrypted with the service's key
        recipient_key = self.service_secrets[recipient]
        ticket = self.generate_ticket(username, shared_key, recipient_key)

        #create and return payload
        payload = {"recipient": recipient, "shared_key": str(shared_key), "ticket": str(ticket)}
        payload_bytes = self.get_payload_bytes(payload)
        payload_encrypted = self.crypto_system.encrypt(payload_bytes, user_session_key)
        return payload_encrypted
    
    def generate_ticket(self, sender, shared_key, key):
        payload = {"sender": sender, "shared_key": str(shared_key)}
        payload_bytes = self.get_payload_bytes(payload)
        ticket = self.crypto_system.encrypt(payload_bytes, key)
        return ticket

    def generate_session_key(self):
        session_key=secrets.token_bytes(16)  # Generates a random 128-bit key using secrets function (https://docs.python.org/3/library/secrets.html)
        return session_key

    #create TGT, which includes username and their session key encrypted with the KDC's key
    def generate_TGT(self, username, session_key):
        payload = {"username": username, "session_key": str(session_key)}
        payload_bytes = self.get_payload_bytes(payload)

        tgt = self.crypto_system.encrypt(payload_bytes, self.K)
        return tgt
    
    def get_payload_bytes(self, payload):
        payload_json = json.dumps(payload)
        return str.encode(payload_json)
    
