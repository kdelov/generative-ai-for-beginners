# here are some suggestions to improve the code:

# - Add input validation to prevent malicious input from being processed by the server. You can use a library like flask-wtf to validate user input and sanitize it before processing.

# - Use environment variables to store sensitive information such as database credentials, API keys, and other secrets. This will prevent the information from being hard-coded in the code and exposed in case of a security breach.

# - Implement error handling to provide meaningful error messages to the user in case of errors. You can use the @app.errorhandler() decorator to handle exceptions and return an error response.

import os
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from dotenv import load_dotenv

# Load .env for local dev; in production, SECRET_KEY comes from environment
load_dotenv()

app = Flask(__name__)

# Use environment variable for secret key
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY", "fallback-secret")

class HelloForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=3)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def hello():
    form = HelloForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        return f'Hello, {name} ({email})!'
    return render_template('form.html', form=form)

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return 'Bad request', 400

@app.errorhandler(500)
def server_error(error):
    return 'Something went wrong on our end.', 500

if __name__ == '__main__':
    app.run(debug=True)