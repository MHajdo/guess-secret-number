import random
import os
from sqla_wrapper import SQLAlchemy
from flask import Flask, render_template, request, make_response

app = Flask(__name__)

db_url = os.getenv("DATABASE_URL", "sqlite:///db.sqlite").replace("postgres://", "postgresql://", 1)
db = SQLAlchemy(db_url)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    secret_number = db.Column(db.Integer, unique=False)


db.create_all()


@app.route("/", methods=["GET"])
def index():
    secret_number = request.cookies.get("secret_number")

    response = make_response(render_template("index.html"))
    if not secret_number:
        new_secret = random.randint(1, 45)
        response.set_cookie("secret_number", str(new_secret))

    return response


@app.route("/result", methods=["POST"])
def result():
    guess = int(request.form.get("guess"))
    secret_number = int(request.cookies.get("secret_number"))

    if guess == secret_number:
        message = f"Congratulations! The secret number is {secret_number}"
        response = make_response(render_template("result.html", message=message))
        response.set_cookie("secret_number", str(random.randint(1, 45)))
        return response
    elif guess > secret_number:
        message = "The secret number is smaller. Try Again"
        return render_template("result.html", message=message)
    elif guess < secret_number:
        message = "The secret number is bigger. Try again."
        return render_template("result.html", message=message)


@app.route('/users')
def users_page():
    users = db.query(User).all()
    return render_template('users.html', users=users)


@app.route('/users/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        secret_num = random.randint(1, 45)
        email_addr = request.form.get('email')
        new_user = User(email=email_addr, secret_number=secret_num)

        new_user.save()

        return render_template('message.html', type='success', message="Successfully created new user", redirect=True)


if __name__ == '__main__':
    app.run(use_reloader=True)
