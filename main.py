from flask import Flask, render_template, flash, request, url_for, redirect, session, jsonify, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pwd import *
import openai
import os
from werkzeug.security import generate_password_hash, check_password_hash
#creates Flask instance
app = Flask(__name__)
openai.api_key = apiKey
messages = []
#DataBase
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
#Create a model
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200), nullable = False)
    email = db.Column(db.String(200), nullable = False, unique = True)
    date_added =db.Column(db.DateTime, default = datetime.utcnow)
    password = db.Column(db.String(50), nullable = False)
    
    #create string
    def __repr__(self):
        return '<Name %r>' % self.name


#create a form class
app.config['SECRET_KEY'] = "WalterWhite"
class NameForm(FlaskForm):
    name = StringField("Whats Your Name", validators = [DataRequired()])
    submit = SubmitField("Submit")


@app.route('/')
def index():
    return render_template('mainPage.html')
    

@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


@app.route('/about')
def about():
    return render_template('about.html')



# ... (other imports and code)

@app.route("/chatBot", methods=("GET", "POST"))
def chatBot():
    global messages

    if request.method == "POST":
        user_input = request.form["user_input"]
        messages.append({
            "sender": "user",
            "content": "Pretend your name is Bo. Bo the Bunny. You are a bunny. Your role today is to be a nice friend who assists others in need of mental help! You will speak in a respective language. You will be able to help others in need of mental help. You will speak in a respective tone.",
            "text": user_input
        })

        conversation = "\n".join([f"User: {msg['text']}" if msg['sender'] == 'user' else f"Bo: {msg['text']}" for msg in messages])
        ai_response = get_ai_response(conversation)

        messages.append({
            "sender": "bot",
            "content": user_input,
            "text": ai_response
        })
        
        return redirect(url_for("chatBot"))

    return render_template("chatBot.html", messages=messages)

def get_ai_response(conversation):
    persona = "Hi, I'm Bo, your helpful friend. Your full name is Bo the Bunny. Your role today is to be a nice friend who assists others in need of mental help! You will speak in a respective language. You will be able to help others in need of mental help. You will speak in a respective tone.You will always remember the users name when they tell you their name."
    prompt = f"{persona}\n{conversation}"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.6,
        max_tokens=150,
    )
    return response.choices[0].text

# ... (other routes and code)

@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the username from the session
    return redirect(url_for('index'))

@app.route('/signUp', methods = ['GET', 'POST'])
def signUp():
    if request.method == "POST":
        userName = request.form.get('username')
        pwd = request.form.get('password')
        email = request.form.get('email')
        
        emailExsist = User.query.filter_by(email = email).first()
        userNameExsist = User.query.filter_by(name = userName).first()
        
        if emailExsist:
            error_message = f"This email ({email}) already exists."
            return render_template('signup.html', error=error_message)
        elif userNameExsist:
            error_message = f"This username ({userName}) already exists."
            return render_template('signup.html', error=error_message)
        elif len(pwd) < 5:
            error_message = "Your password is too short. It must be at least 8 characters long."
            return render_template('signup.html', error=error_message)
        else:
            newUser = User(name = userName, email = email, password = generate_password_hash(pwd, method='sha256'))
            db.session.add(newUser)
            db.session.commit()
                  
        print(userName, pwd, email)
        return redirect(url_for('index'))
    return render_template('signUp.html')

@app.route('/signIn', methods=['GET', 'POST'])
def signIn():
    if request.method == "POST":
        userName = request.form.get('username')
        pwd = request.form.get('password')
        print(userName, pwd)
        user = User.query.filter_by(name=userName).first()
        if user is None:
            error_message = f"This username ({userName}) doesn't exist. Please try again"
            return render_template('signIn.html', error=error_message)
        else:
            print("Username Exists")
            if check_password_hash(user.password, pwd):
                session['username'] = user.name  # Store the username in the session
                return redirect(url_for('index'))
            else:
                print("Incorrect password")
                error_message = "Incorrect password. Please try again"
                return render_template('signIn.html', error=error_message)
    return render_template('signIn.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

