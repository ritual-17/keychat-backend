import secrets
import json

import AES

class KDC:
    def __init__(self, user_secrets):
        self.user_secrets = user_secrets #users keys
        self.service_secrets = {"server": self.generate_session_key()} #service keys
        self.K = secrets.token_bytes(16) #the KDC's key
        self.crypto_system = AES.AES() #our encryption algorithm
        self.active_users = {} #active users and their connections

    def encrypt_shared_key(self, plaintext, shared_key):
        return self.crypto_system.encrypt(plaintext, shared_key)

    def decrypt_shared_key(self, ciphertext, shared_key):
        return self.crypto_system.decrypt(ciphertext, shared_key)

    #return encrypted TGT payload, including session key and TGT encrypted using the user's secret key
    def register(self, username):
        session_key = self.generate_session_key()
        tgt = self.generate_TGT(username, session_key)

        payload = {"session_key": str(session_key), "tgt": str(tgt)}
        payload_bytes = self.get_payload_bytes(payload)

        return self.crypto_system.encrypt(session_key, self.user_secrets[username]),self.crypto_system.encrypt(tgt, self.user_secrets[username])
    
    def update_key(self, tgt):
        #decrypt tgt using KDC key to get old session key of user
        tgt_decrypted = self.crypto_system.decrypt(tgt, self.K)
        tgt_decrypted_json = json.loads(tgt_decrypted)
        username = tgt_decrypted_json["username"]
        session_key = eval(tgt_decrypted_json["session_key"])

        #generate new session key
        new_session_key = self.generate_session_key()
        new_tgt = self.generate_TGT(username, new_session_key)

        #encrypt and return new session key and new tgt
        session_key_response = self.crypto_system.encrypt(new_session_key, session_key)
        tgt_response = self.crypto_system.encrypt(new_tgt, session_key)
        return session_key_response, tgt_response




    def add_user(self, username, sid):
        self.active_users[sid] = username

    def remove_user(self, sid):
        self.active_users.pop(sid)
    
    #user is requesting a ticket to talk to a service
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
        recipient_response = self.crypto_system.encrypt(recipient, user_session_key)
        shared_key_response = self.crypto_system.encrypt(shared_key, user_session_key)
        ticket_response = self.crypto_system.encrypt(ticket, user_session_key)
        return recipient_response, shared_key_response, ticket_response
    
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
    
