from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET'
app.config['WTF_CSRF_ENABLED'] = False


import flaskr.routes