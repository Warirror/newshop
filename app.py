from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "sulekha_premium_key"

# Database Configuration (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sulekha.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 1. User Model (ലോഗിൻ വിവരങ്ങൾ സേവ് ചെയ്യാൻ)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# 2. Product Model (സാരികളുടെ വിവരങ്ങൾ സേവ് ചെയ്യാൻ)
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(20), nullable=False)
    img = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)

# ഡാറ്റാബേസ് ക്രിയേറ്റ് ചെയ്യാൻ (ആദ്യ തവണ മാത്രം)
with app.app_context():
    db.create_all()
    # ഡമ്മി പ്രോഡക്റ്റുകൾ ആഡ് ചെയ്യണമെങ്കിൽ ഇവിടെ ചെയ്യാം
    if not Product.query.first():
        p1 = Product(name="Royal Wedding Silk", price="24,500", img="saree1.jpg", category="Bridal")
        p2 = Product(name="Golden Kasavu", price="8,900", img="saree2.jpg", category="Traditional")
        db.session.add_all([p1, p2])
        db.session.commit()

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shop')
def shop():
    all_products = Product.query.all() # SQL-ൽ നിന്ന് പ്രോഡക്റ്റുകൾ എടുക്കുന്നു
    return render_template('index.html', products=all_products) # index-ൽ തന്നെ ഷോപ്പ് ഉള്ളതുകൊണ്ട്

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    # യൂസർ ഓൾറെഡി ഉണ്ടോ എന്ന് നോക്കുന്നു
    user_exists = User.query.filter_by(email=email).first()
    if user_exists:
        flash("Email already registered!")
        return redirect(url_for('index'))

    # പാസ്‌വേഡ് സെക്യൂർ ആക്കി ഡാറ്റാബേസിലേക്ക് മാറ്റുന്നു
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(name=name, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    flash("Account created! Please login.")
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['user_name'] = user.name
        return redirect(url_for('index'))
    else:
        flash("Invalid email or password!")
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
