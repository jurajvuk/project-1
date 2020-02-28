import os

from flask import Flask, session, render_template, request, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    if session.get("id"):
        return render_template("index.html", id = session.get("id"))
    else:
        return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form.get("username")
        if username == "":
            return render_template('error.html', message = "Username required!")
        password = request.form.get("password")
        if password == "":
            return render_template('error.html', message = "Password required!")
        if db.execute("SELECT * FROM users WHERE username=:username", {"username": username}).rowcount != 0:
            userCheck = db.execute("SELECT id FROM users WHERE username=:username", {"username": username}).fetchall()
            session["id"] = userCheck[0].id
            return render_template("index.html", id = session["id"])

@app.route("/logout", methods=["GET"])
def logout():
    session["id"] = 0
    return redirect('/')

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        if username == "":
            return render_template('error.html', message = "Username required!")
        password = request.form.get("password")
        if password == "":
            return render_template('error.html', message = "Password required!")
        confirmPassword = request.form.get("confirm-password")
        if confirmPassword != password:
            return render_template('error.html', message = "Passwords don't match!")
        if db.execute("SELECT * FROM users WHERE username=:username", {"username": username}).rowcount > 0:
            return render_template('error.html', message = "Username already taken!")
        db.execute("INSERT INTO users (username, password) VALUES(:username, :password)", {"username": username, "password": password})
        db.commit()
        return render_template("login.html")
            

@app.route("/search", methods=["POST"])
def search():
    search = "%" + request.form.get("search") + "%"
    books = db.execute("SELECT * FROM books WHERE isbn LIKE :search OR author LIKE :search OR title LIKE :search", {"search": search}).fetchall()
    imageLink = "http://covers.openlibrary.org/b/isbn/"
    #res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "JqAdwcwlyIF7qMIs3PSHGA", "isbns": "9781632168146"})
    if books:
        return render_template("result.html", books = books, imageLink = imageLink, id = session["id"])
    else:
        return render_template("index.html")
