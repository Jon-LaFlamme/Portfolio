from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flaskr.extensions import db
from flaskr.extensions import cosmos_db
from flask_jsglue import JSGlue

csrf = CSRFProtect()
app = Flask(__name__)
jsglue = JSGlue(app)
app.config['SECRET_KEY'] = 'SECRET'
app.config['WTF_CSRF_ENABLED'] = False
csrf.init_app(app)
db.init_app(app)
cosmos_db.init_app(app)

import flaskr.routes