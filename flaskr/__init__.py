from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_jsglue import JSGlue

csrf = CSRFProtect()
app = Flask(__name__)
jsglue = JSGlue(app)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET'
app.config['WTF_CSRF_ENABLED'] = False
csrf.init_app(app)


import flaskr.routes