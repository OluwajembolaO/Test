from flask import Flask, render_template, flash, request, url_for, redirect, session, jsonify, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pwd import *
import openai
import os
#creates Flask instance
app = Flask(__name__)
openai.api_key = apiKey
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

@app.route("/chatBot", methods=("GET", "POST"))
def chatBot():
    if request.method == "POST":
        animal = request.form["animal"]
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=generate_prompt(animal),
            temperature=0.6,
        )
        return redirect(url_for("chatBot", result=response.choices[0].text))

    result = request.args.get("result")
    return render_template("chatBot.html", result=result)


def generate_prompt(animal):
    return """Suggest three names for an animal that is a superhero.

    Animal: Cat
    Names: Captain Sharpclaw, Agent Fluffball, The Incredible Feline
    Animal: Dog
    Names: Ruff the Protector, Wonder Canine, Sir Barks-a-Lot
    Animal: {}
    Names:""".format(
        animal.capitalize()
    )

@app.route('/signIn', methods=['GET', 'POST'])
def signIn():
    if request.method == "POST":
        # Perform login authentication here, for simplicity, let's just assume it's successful
        username = request.form.get('username')
        session['username'] = username  # Store the username in the session
        return redirect(url_for('index'))
    return render_template('signIn.html')


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
        if len(pwd) < 5:
            error_message = "Your password is too short. It must be at least 8 characters long."
            return render_template('signup.html', error=error_message)
        print(userName, pwd, email)
        return redirect(url_for('index'))
    return render_template('signUp.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

