from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '6b075fed29e7bc9dad7cec59162850c6'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grocerystore.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from GroceryStore import routes, models, forms

if __name__ == "__main__":
    app.run(debug=True)
