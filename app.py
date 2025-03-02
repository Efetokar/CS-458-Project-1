from flask import Flask, render_template, request, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
import re
import sqlite3

app = Flask(__name__)
app.secret_key = "super_secret_key"  

oauth = OAuth(app)
# update according to the information given
app.config["GOOGLE_CLIENT_ID"] = "hello"
app.config["GOOGLE_CLIENT_SECRET"] = "hello"

google = oauth.register(
    name='google',
    client_id=app.config["GOOGLE_CLIENT_ID"],
    client_secret=app.config["GOOGLE_CLIENT_SECRET"],
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v2/',
    client_kwargs={
        'scope': 'openid email profile'
    },
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs'
)

# Database helper functions
def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_users_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def seed_user():
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO users (email, phone, password)
            VALUES (?, ?, ?)
        ''', ("test@example.com", "05555555555", "P@ssw0rd!"))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()

create_users_table()
seed_user()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    user_input = request.form.get('user_input')
    password = request.form.get('password')
    
    if not user_input or not password:
        return render_template('login.html', error="Error: Required fields are empty!")

    if re.search(r"(?:--|or|and|;|drop\s+table)", user_input, re.IGNORECASE):
        return render_template('login.html', error="Error: Invalid characters detected!")
    
    if re.search(r"<.*?>", user_input) or re.search(r"<.*?>", password):
        return render_template('login.html', error="Error: XSS attack prevented!")
    
    if len(password) < 6:
        return render_template('login.html', error="Error: Password must be at least 6 characters!")
    
    if len(password) > 50:
        return render_template('login.html', error="Error: Password is too long!")
    
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ? OR phone = ?", (user_input, user_input)).fetchone()
    conn.close()
    
    if user and password == user["password"]:
        session['user'] = user["email"]  
        return redirect(url_for('welcome'))
    else:
        return render_template('login.html', error="Error: Email/Phone or password is incorrect!")

@app.route('/login/google')
def login_with_google():
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/google/callback')
def google_callback():
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    session['user'] = user_info['email']
    
    return """
    <script>
        if (window.opener) {
            window.opener.location.href = '/welcome';
            window.close();
        } else {
            window.location.href = '/welcome';
        }
    </script>
    """

@app.route('/welcome')
def welcome():
    if 'user' not in session:
        return redirect(url_for('login'))
    return f"Welcome, {session['user']}!"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)