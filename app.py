from flask import Flask, request, jsonify
import sqlite3
import requests

app = Flask(__name__)

# Create a SQLite database
conn = sqlite3.connect('user_database.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        age INTEGER,
        gender TEXT,
        email TEXT,
        phone TEXT,
        birth_date TEXT
    )
''')
conn.commit()
conn.close()

# Endpoint to search for users
@app.route('/api/users', methods=['GET'])
def search_users():
    first_name = request.args.get('first_name')
    if not first_name:
        return jsonify({'error': 'Missing mandatory query parameter: first_name'}), 400
    
    conn = sqlite3.connect('user_database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE first_name LIKE ?", (f'{first_name}%',))
    matching_users = cursor.fetchall()
    
    if matching_users:
        conn.close()
        users_list = []
        for user in matching_users:
            user_dict = {
                'id': user[0],
                'first_name': user[1],
                'last_name': user[2],
                'age': user[3],
                'gender': user[4],
                'email': user[5],
                'phone': user[6],
                'birth_date': user[7]
            }
            users_list.append(user_dict)
        return jsonify(users_list)
    else:
        conn.close()
        response = requests.get(f"https://dummyjson.com/users/search?q={first_name}")
        dummy_users = response.json()
        
        conn = sqlite3.connect('user_database.db')
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT INTO users (first_name, last_name, age, gender, email, phone, birth_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', [(user['first_name'], user['last_name'], user['age'], user['gender'], user['email'], user['phone'], user['birth_date']) for user in dummy_users])
        conn.commit()
        conn.close()
        
        return jsonify(dummy_users)

if __name__ == '__main__':
    app.run(debug=True)
