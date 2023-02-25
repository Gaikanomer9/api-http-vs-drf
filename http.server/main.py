from http.server import HTTPServer
import sqlite3
from api import APIServer

# Create the database and tables
conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY, title TEXT, content TEXT, author_id INTEGER, FOREIGN KEY(author_id) REFERENCES users(id))')
conn.commit()
conn.close()

# Create the API server
server = HTTPServer(('localhost', 8080), APIServer)

# Start the server
print('Starting server...')
server.serve_forever()
