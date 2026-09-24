from flask import Flask, render_template, request, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "cybersecurity_secret_key"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="cybersecurity_db"
)


@app.route("/")
def home():
    return "Cybersecurity Complaint Management System"


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]

        if len(username) < 3:
            return "Username must contain at least 3 characters!"

        if len(password) < 6:
            return "Password must contain at least 6 characters!"

        hashed_password = generate_password_hash(password)

        cursor = db.cursor()

        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, hashed_password)
        )

        db.commit()
        cursor.close()

        return "Registration successful!"

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        email = request.form["email"].strip()
        password = request.form["password"]

        cursor = db.cursor()

        cursor.execute(
            "SELECT id, password FROM users WHERE email = %s",
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()

        if user and check_password_hash(user[1], password):

            session["user_id"] = user[0]

            return "Login successful!"

        return "Invalid email or password!"

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return "Please login first!"

    return render_template("dashboard.html")


@app.route("/complaints/add", methods=["GET", "POST"])
def add_complaint():

    if "user_id" not in session:
        return "Please login first!"

    if request.method == "POST":

        title = request.form["title"].strip()
        description = request.form["description"].strip()
        complaint_type = request.form["complaint_type"]
        severity = request.form["severity"]

        if len(title) < 3:
            return "Title must contain at least 3 characters!"

        if len(description) < 10:
            return "Description must contain at least 10 characters!"

        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO complaints
            (title, description, complaint_type, severity, reported_by)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                title,
                description,
                complaint_type,
                severity,
                session["user_id"]
            )
        )

        db.commit()
        cursor.close()

        return "Complaint submitted successfully!"

    return render_template("add_complaint.html")


@app.route("/complaints")
def complaints():

    if "user_id" not in session:
        return "Please login first!"

    cursor = db.cursor()

    cursor.execute(
        """
        SELECT * FROM complaints
        WHERE reported_by = %s
        ORDER BY id DESC
        """,
        (session["user_id"],)
    )

    complaints_data = cursor.fetchall()

    cursor.close()

    return render_template(
        "complaints.html",
        complaints=complaints_data
    )


@app.route("/complaints/delete/<int:id>")
def delete_complaint(id):

    if "user_id" not in session:
        return "Please login first!"

    cursor = db.cursor()

    cursor.execute(
        """
        DELETE FROM complaints
        WHERE id = %s AND reported_by = %s
        """,
        (id, session["user_id"])
    )

    db.commit()
    cursor.close()

    return "Complaint deleted successfully!"


@app.route("/complaints/edit/<int:id>", methods=["GET", "POST"])
def edit_complaint(id):

    if "user_id" not in session:
        return "Please login first!"

    cursor = db.cursor()

    if request.method == "POST":

        title = request.form["title"].strip()
        description = request.form["description"].strip()
        complaint_type = request.form["complaint_type"]
        severity = request.form["severity"]
        status = request.form["status"]

        if len(title) < 3:
            cursor.close()
            return "Title must contain at least 3 characters!"

        if len(description) < 10:
            cursor.close()
            return "Description must contain at least 10 characters!"

        cursor.execute(
            """
            UPDATE complaints
            SET title = %s,
                description = %s,
                complaint_type = %s,
                severity = %s,
                status = %s
            WHERE id = %s AND reported_by = %s
            """,
            (
                title,
                description,
                complaint_type,
                severity,
                status,
                id,
                session["user_id"]
            )
        )

        db.commit()
        cursor.close()

        return "Complaint updated successfully!"

    cursor.execute(
        """
        SELECT * FROM complaints
        WHERE id = %s AND reported_by = %s
        """,
        (id, session["user_id"])
    )

    complaint = cursor.fetchone()

    cursor.close()

    if complaint is None:
        return "Complaint not found!"

    return render_template(
        "edit_complaint.html",
        complaint=complaint
    )


if __name__ == "__main__":
    app.run(debug=True)