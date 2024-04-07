# keychat-backend
Backend for KeyChat project for SFWRENG 3A04

## Getting started
* `pip install -r requirements.txt`

# Backend Server Testing Documentation

This README provides instructions on how to run client scripts to test the functionality of the backend server for chat, contacts, and employee management features.

## Getting Started

Ensure your backend server is up and running before executing the client scripts. The server should be listening on the designated port, typically `http://localhost:8080`.

## Prerequisites

- Python installed on your machine.
- Access to the terminal or command prompt.
- The backend server running locally.

## Running the Client Scripts

We have provided three client scripts to test different functionalities of the backend server: `chat_client.py`, `contacts_client.py`, and `employee_client.py`. Each script simulates interactions with the server to test its respective functionality.

### Chat Client

The `chat_client.py` script tests the chat functionality, including creating chats, sending messages, and fetching chat history.

To run the chat client script:

```bash
python chat_client.py
