import random
import uuid
import hashlib
from sqla_wrapper import SQLAlchemy
from flask import Flask, render_template, request, make_response, redirect, url_for

app = Flask(__name__)

db = SQLAlchemy("sqlite:///database.sqlite")


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String, unique=False)
    secret_number = db.Column(db.Integer, unique=False)
    session_token = db.Column(db.String, unique=True)


db.create_all()


def get_user():
    token = request.cookies.get('session_token')
    if token is None:
        return None
    user = db.query(User).filter_by(session_token=token).first()
    return user


@app.route("/", methods=["GET"])
def index():
    user = get_user()
    secret_number = request.cookies.get("secret_number")

    response = make_response(render_template("index.html", user=user))
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
        password1 = request.form.get('pass1')
        password2 = request.form.get('pass2')
        if password2 != password1:
            return render_template('register.html', errMsg="The passwords did not match")
        if email_addr == '' or email_addr is None:
            return render_template('register.html', errMsg="Email field should be filled with a valid email address.")

        hashed_pass = hashlib.sha256(password1.encode()).hexdigest()

        new_user = User(email=email_addr, secret_number=secret_num, password=hashed_pass)

        new_user.save()

        return render_template('message.html', type='success', message="Successfully created new user", redirect=True)


@app.route('/users/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email_addr = request.form.get('email')
        password = request.form.get('password')

        user = db.query(User).filter_by(email=email_addr).first()

        if user is None:
            return render_template('login.html', errMsg='Login credentials were not correct!')

        hashed_pass = hashlib.sha256(password.encode()).hexdigest()

        if user.password == hashed_pass:
            response = make_response(
                render_template('message.html', type='success', message='Successfully logged in', redirect=True)
            )
            session_token = str(uuid.uuid4())

            user.session_token = session_token
            response.set_cookie('session_token', session_token)
            user.save()
            return response
        else:
            return render_template('login.html', errMsg='Login credentials were not correct!')


@app.route('/users/profile')
def profile_page():
    user = get_user()
    if user is None:
        return redirect(url_for('login'))
    else:
        return render_template('profile_page.html', user=user)


@app.route('/users/profile/edit', methods=['GET', 'POST'])
def profile_page_edit():
    user = get_user()
    if user is None:
        return redirect(url_for('login'))
    else:
        if request.method == 'GET':
            return render_template('profile_page_edit.html', user=user)
        else:
            email = request.form.get('email')
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')

            if email != user.email:
                user.email = email

            if password2 == password1:
                hashed_pass = hashlib.sha256(password1.encode()).hexdigest()
                user.password = hashed_pass
            else:
                return render_template('profile_page_edit.html', user=user, message='The passwords did not match')

            user.save()
            return redirect(url_for('profile_page'))


@app.route('/users/profile/delete', methods=['GET', 'POST'])
def profile_page_delete():
    if request.method == 'POST':
        user = get_user()
        user.delete()
        return render_template('message.html', message='Account deleted', redirectHome=True)
    else:
        return render_template('profile_page_delete.html')


@app.route('/user/<user_id>', methods=["GET"])
def user_details(user_id):
    user = db.query(User).get(int(user_id))
    return render_template('user_details.html', user=user)


if __name__ == '__main__':
    app.run(use_reloader=True)
