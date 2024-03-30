import time

import AES

class KDC:
    def __init__(self):
        self.user_secrets = {} #users keys
        self.K = 123 #the KDC's key - TO BE IMPLEMENTED
        self.crypto_system = AES() #our encryption algorithm

    #register the user by adding their secret key to the system
    def register(self, username, secret):
        self.user_secrets[username] = secret

    #return encrypted TGT payload, including session key and TGT encrypted using the user's secret key
    def return_TGT(self, username):
        session_key = self.generate_session_key()
        tgt = self.generate_TGT(username, session_key)
        payload = str(session_key) + "," + str(tgt)
        response = self.crypto_system.encrypt(self.user_secrets[username],payload)
        return response
    
    #for when user is requesting a ticket to talk to another user
    def return_ticket(self, username, recipient, tgt, authenticator):
        if recipient not in self.user_secrets:
            return None
        #generate shared key
        shared_key = self.generate_session_key()
        #decrypt tgt to get session key of user
        tgt_decrypted = self.crypto_system.decrypt(self.K, tgt).split(",") #should be in format "username,key"
        user_session_key = tgt_decrypted[1] #session key will be second element
        #authenticating time stamp
        timestamp = self.crypto_system.decrypt(user_session_key, authenticator)
        now = time.time()
        if abs(now-timestamp) > 300: #must be within 5 minutes
            return None
        #generate ticket and create payload
        ticket = self.generate_ticket(username, shared_key, self.K)
        payload = recipient + "," + str(shared_key) + "," + ticket
        payload_encrypted = self.crypto_system.encrypt(user_session_key,payload)
        return payload_encrypted

    #when a user receives a ticket from another user, it needs the ticket to be encrypted with its session key
    def verify_ticket(self, tgt, ticket, authenticator):
        tgt_decrypted = self.crypto_system.decrypt(self.K, tgt).split(",")
        session_key = tgt_decrypted[1]

        #authenticating time stamp
        timestamp = self.crypto_system.decrypt(session_key, authenticator)
        now = time.time()
        if abs(now-timestamp) > 300: #5 minutes
            return None
        
        ticket_decrypted = self.crypto_system.decrypt(self.K, ticket)
        new_ticket = self.crypto_system.encrypt(session_key, ticket_decrypted)
        return new_ticket
    
    def generate_ticket(self, sender, shared_key, key):
        payload = sender + "," + str(shared_key)
        ticket = self.crypto_system.encrypt(key, payload)
        return ticket

    #to be implemented
    def generate_session_key(self):
        session_key = 123
        return session_key

    #create TGT, which includes username and their session key encrypted with the KDC's key
    def generate_TGT(self, username, session_key):
        payload = username + "," + str(session_key)
        tgt = self.crypto_system.encrypt(self.K, payload)
        return tgt
    