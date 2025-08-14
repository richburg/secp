# Simple and Efficient Chatting Protocol - SECP

#### Dependencies
- Python standard library: `logging`, `typing`, `asyncio`, `re`

#### Boot instructions
As I stated earlier, no external package is used in this project. So having Python 3+ installed will be enough. First of all, you need to configure the server in `server/config.py` and then you can easily run it with `python3 -m server`.

### Protocol
Uses plain-text communication over TCP streams. Every data received/sent over the connection is called a message. Every message has a `type` and optionally a few `arguments`. Because of its simplicity, the message format is identical both for client and server.