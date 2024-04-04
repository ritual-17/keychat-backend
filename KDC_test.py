import KDC
import secrets
import AES
import json

crypto_system = AES.AES()

user_secrets = {"Bob": secrets.token_bytes(16)}
service_secrets = {"service": secrets.token_bytes(16)}

kdc = KDC.KDC(user_secrets, service_secrets)

def test_return_TGT():
    secret_key = user_secrets["Bob"]
    tgt = kdc.return_TGT("Bob")
    decrypted_tgt = crypto_system.decrypt(tgt, secret_key)
    decrypted_tgt_json = json.loads(decrypted_tgt)
    session_key = eval(decrypted_tgt_json["session_key"])
    assert len(session_key) == 16

def test_return_ticket():
    #get TGT payload
    payload = kdc.return_TGT("Bob")
    decrypted_payload = crypto_system.decrypt(payload, user_secrets["Bob"])
    decrypted_payload_json = json.loads(decrypted_payload)

    #parse session key and TGT
    session_key = eval(decrypted_payload_json["session_key"])
    tgt = eval(decrypted_payload_json["tgt"])

    #get ticket payload
    ticket_payload = kdc.return_ticket("Bob", "service", tgt)
    decrypted_ticket_payload = crypto_system.decrypt(ticket_payload, session_key)
    decrypted_ticket_payload_json = json.loads(decrypted_ticket_payload)

    #parse shared key and ticket
    recipient = decrypted_ticket_payload_json["recipient"]
    assert recipient == "service"
    shared_key = eval(decrypted_ticket_payload_json["shared_key"])
    ticket = eval(decrypted_ticket_payload_json["ticket"])

    #send ticket to service
    service_shared_key = service_receive_ticket_test(ticket)
    assert shared_key == service_shared_key

    #send message to service
    message = "Hello, service!"
    encrypted_message = crypto_system.encrypt(message.encode(), shared_key)
    decrypted_message = crypto_system.decrypt(encrypted_message, service_shared_key).decode()
    assert message == decrypted_message
    
def service_receive_ticket_test(ticket):
    #decrypt ticket using service's secret key
    decrypted_ticket = crypto_system.decrypt(ticket, service_secrets["service"])
    decrypted_ticket_json = json.loads(decrypted_ticket)
    sender = decrypted_ticket_json["sender"]
    shared_key = eval(decrypted_ticket_json["shared_key"])
    return shared_key

test_return_TGT()
test_return_ticket()