from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# സെക്യൂരിറ്റി കീ - ഇത് സെഷൻ മാനേജ്‌മെന്റിന് അത്യാവശ്യമാണ്
app.secret_key = "sulekha_royal_secret_key" 

# Database Configuration (SQLite)
# പ്രോജക്റ്റ് ഫോൾഡറിൽ 'sulekha.db' എന്ന പേരിൽ ഡാറ്റാബേസ് ഫയൽ ഉണ്ടാകും
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sulekha.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELS (ഡാറ്റാബേസ് സ്ട്രക്ചർ) ---

# 1. User Model: ലോഗിൻ വിവരങ്ങൾ സൂക്ഷിക്കാൻ
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# 2. Product Model: സാരികളുടെ വിവരങ്ങൾ സൂക്ഷിക്കാൻ
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(20), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(50), nullable=False)

# ഡാറ്റാബേസ് ക്രിയേറ്റ് ചെയ്യാനും ഡമ്മി ഡാറ്റ ആഡ് ചെയ്യാനും
with app.app_context():
    db.create_all()
    # ഡാറ്റാബേസ് കാലിയാണെങ്കിൽ മാത്രം ചില സാമ്പിൾ പ്രോഡക്റ്റുകൾ ആഡ് ചെയ്യും
    if not Product.query.first():
        sample_products = [
            Product(name="Crimson Kanchipuram", price="28,500", img_url="https://images.pexels.com/photos/15712165/pexels-photo-15712165.jpeg", category="Bridal"),
            Product(name="Royal Ivory Kasavu", price="12,200", img_url="https://images.pexels.com/photos/14624458/pexels-photo-14624458.jpeg", category="Traditional"),
            Product(name="Emerald Banarasi Silk", price="15,800", img_url="https://images.pexels.com/photos/11050215/pexels-photo-11050215.jpeg", category="Luxury"),
            Product(name="Golden Wedding Weave", price="32,000", img_url="https://images.pexels.com/photos/11050212/pexels-photo-11050212.jpeg", category="Bridal")
        ]
        db.session.add_all(sample_products)
        db.session.commit()

# --- ROUTES (പേജുകൾ) ---

# 1. ഹോം പേജ്
@app.route('/')
def index():
    featured = Product.query.limit(4).all()
    return render_template('index.html', products=featured)

# 2. ഷോപ്പ് / കളക്ഷൻ പേജ്
@app.route('/shop')
def shop():
    all_products = Product.query.all()
    return render_template('shop.html', products=all_products)

# 3. ഗാലറി പേജ് (മോഡൽ ഷൂട്ടുകൾ കാണിക്കാൻ)
@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

# 4. എബൗട്ട് പേജ് (ഹിസ്റ്ററി & ട്രസ്റ്റ്)
@app.route('/about')
def about():
    return render_template('about.html')

# 5. കോൺടാക്റ്റ് പേജ്
@app.route('/contact')
def contact():
    return render_template('contact.html')

# 6. ലോഗിൻ സിസ്റ്റം
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash(f"Welcome back, {user.name}!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid email or password. Please try again.", "danger")
            return redirect(url_for('login'))
            
    return render_template('login.html')

# 7. സൈൻഅപ്പ് സിസ്റ്റം
@app.route('/signup', methods=['POST'])
def signup():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    user_exists = User.query.filter_by(email=email).first()
    if user_exists:
        flash("This email is already registered!", "warning")
        return redirect(url_for('login'))

    # പാസ്‌വേഡ് ഹാഷ് ചെയ്ത് സൂക്ഷിക്കുന്നു (സെക്യൂരിറ്റിക്ക് വേണ്ടി)
    hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(name=name, email=email, password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    
    flash("Account created successfully! Please login.", "success")
    return redirect(url_for('login'))

# 8. പ്രൊഫൈൽ പേജ് (ലോഗിൻ ചെയ്തവർക്ക് മാത്രം)
@app.route('/profile')
def profile():
    if 'user_name' not in session:
        flash("Please login to access your profile", "info")
        return redirect(url_for('login'))
    return render_template('profile.html')

# 9. ലോഗൗട്ട്
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

# 10. 404 Error Page (തെറ്റായ ലിങ്കിൽ പോയാൽ ഹോം പേജിലേക്ക് വിടാൻ)
@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('index'))

if __name__ == '__main__':
    # debug=True കൊടുക്കുന്നത് ഡെവലപ്‌മെന്റ് സമയത്ത് മാറ്റങ്ങൾ പെട്ടെന്ന് കാണാനാണ്
    app.run(debug=True)
