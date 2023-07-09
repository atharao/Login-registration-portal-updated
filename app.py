from flask import Flask, render_template, request, g
import sqlite3

app = Flask(__name__)
app.config['DATABASE'] = 'database.db'
app.config['SECRET_KEY'] = 'your_secret_key'

def create_user_table():
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()

    # Create the user table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL
                    )''')

    conn.commit()
    conn.close()

def insert_user(username, password):
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()

    # Insert the user into the users table
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))

    conn.commit()
    conn.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get the username and password from the form data
        username = request.form.get('username')
        password = request.form.get('password')

        # Perform any necessary validation or checks

        # Check if the username already exists in the database
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            error = 'Username already exists. Please choose a different username.'
            return render_template('register.html', error=error)

        # Insert the new user into the database
        insert_user(username, password)

        return render_template('register_success.html')

    else:
        return render_template('register.html')

# Database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    return db

# Create the user table if it doesn't exist
def init_db():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    db.commit()

# Close the database connection
@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Home page
@app.route('/')
def index():
    return render_template("index.html")

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()

        if user:
            return render_template('login_success.html')
        else:
            error = 'Invalid username or password.'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Display all users
@app.route('/users')
def users():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()

    return render_template('users.html', users=users)

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
