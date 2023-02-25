import http.server
import json
import sqlite3
import urllib.parse


class APIServer(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        if path == '/users':
            users = self.get_users()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(users).encode('utf-8'))
        elif path.startswith('/users/'):
            user_id = int(path.split('/')[2])
            user = self.get_user(user_id)
            if user:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(user).encode('utf-8'))
            else:
                self.send_error(404, 'User not found')
        elif path == '/posts':
            posts = self.get_posts()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(posts).encode('utf-8'))
        elif path.startswith('/posts/'):
            post_id = int(path.split('/')[2])
            post = self.get_post(post_id)
            if post:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(post).encode('utf-8'))
            else:
                self.send_error(404, 'Post not found')
        else:
            self.send_error(404, 'Invalid path')

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = json.loads(post_data)

        if path == '/users':
            user = self.create_user(data)
            if user:
                self.send_response(201)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(user).encode('utf-8'))
            else:
                self.send_error(400, 'Invalid data')
        elif path == '/posts':
            post = self.create_post(data)
            if post:
                self.send_response(201)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(post).encode('utf-8'))
            else:
                self.send_error(400, 'Invalid data')
        else:
            self.send_error(404, 'Invalid path')

    def do_PUT(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        content_length = int(self.headers.get('Content-Length', 0))
        put_data = self.rfile.read(content_length).decode('utf-8')
        data = json.loads(put_data)

        if path.startswith('/users/'):
            user_id = int(path.split('/')[2])
            user = self.get_user(user_id)
            if not user:
                self.send_error(404, 'User not found')
                return

            # check if the requesting user is the author of the post
            if data.get('author_id') and data['author_id'] != user['id']:
                self.send_error(401, 'Unauthorized')
                return

            updated_user = self.update_user(user_id, data)
            if updated_user:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(updated_user).encode('utf-8'))
            else:
                self.send_error(400, 'Invalid data')
        elif path.startswith('/posts/'):
            post_id = int(path.split('/')[2])
            post = self.get_post(post_id)
            if not post:
                self.send_error(404, 'Post not found')
                return

            # check if the requesting user is the author of the post
            if data.get('author_id') and data['author_id'] != post['author_id']:
                self.send_error(401, 'Unauthorized')
                return

            updated_post = self.update_post(post_id, data)
            if updated_post:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(updated_post).encode('utf-8'))
            else:
                self.send_error(400, 'Invalid data')
        else:
            self.send_error(404, 'Invalid path')

    def do_DELETE(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path.startswith('/users/'):
            user_id = int(path.split('/')[2])
            user = self.get_user(user_id)
            if not user:
                self.send_error(404, 'User not found')
                return


            deleted_user = self.delete_user(user_id)
            if deleted_user:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(deleted_user).encode('utf-8'))
            else:
                self.send_error(400, 'Invalid data')
        elif path.startswith('/posts/'):
            post_id = int(path.split('/')[2])
            post = self.get_post(post_id)
            if not post:
                self.send_error(404, 'Post not found')
                return

            # check if the requesting user is the author of the post
            # if post['author_id'] != post_id:
            #     self.send_error(401, 'Unauthorized')
            #     return

            deleted_post = self.delete_post(post_id)
            if deleted_post:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(deleted_post).encode('utf-8'))
            else:
                self.send_error(400, 'Invalid data')
        else:
            self.send_error(404, 'Invalid path')

    def get_users(self):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users')
        users = [{'id': row[0], 'name': row[1], 'email': row[2]} for row in c.fetchall()]
        conn.close()
        return users

    def get_user(self, user_id):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = c.fetchone()
        conn.close()
        if user:
            return {'id': user[0], 'name': user[1], 'email': user[2]}
        else:
            return None

    def create_user(self, data):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (name, email) VALUES (?, ?)',
                  (data['name'], data['email']))
        user_id = c.lastrowid
        conn.commit()
        conn.close()
        return {'id': user_id, 'name': data['name'], 'email': data['email'], }

    def update_user(self, user_id, data):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('UPDATE users SET name = ?, email = ? WHERE id = ?',
                  (data['name'], data['email'], user_id))
        conn.commit()
        updated_rows = c.rowcount
        conn.close()
        if updated_rows > 0:
            return {'id': user_id, 'name': data['name'], 'email': data['email']}
        else:
            return None

    def delete_user(self, user_id):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        deleted_rows = c.rowcount
        conn.close()
        if deleted_rows > 0:
            return {'id': user_id}
        else:
            return None

    def get_posts(self):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM posts')
        posts = [{'id': row[0], 'title': row[1], 'content': row[2], 'author_id': row[3]} for row in c.fetchall()]
        conn.close()
        return posts

    def get_post(self, post_id):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
        post = c.fetchone()
        conn.close()
        if post:
            return {'id': post[0], 'title': post[1], 'content': post[2], 'author_id': post[3]}
        else:
            return None

    def create_post(self, data):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO posts (title, content, author_id) VALUES (?, ?, ?)',
                  (data['title'], data['content'], data['author_id']))
        post_id = c.lastrowid
        conn.commit()
        conn.close()
        return {'id': post_id, 'title': data['title'], 'content': data['content'], 'author_id': data['author_id']}

    def update_post(self, post_id, data):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?',
                  (data['title'], data['content'], post_id))
        conn.commit()
        updated_rows = c.rowcount
        conn.close()
        if updated_rows > 0:
            return {'id': post_id, 'title': data['title'], 'content': data['content'], 'author_id': data['author_id']}
        else:
            return None

    def delete_post(self, post_id):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()
        deleted_rows = c.rowcount
        conn.close()
        if deleted_rows > 0:
            return {'id': post_id}
        else:
            return None

