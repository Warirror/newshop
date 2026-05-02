from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "sulekha_secret_key"

# Sample Database (നിനക്ക് ഇത് പിന്നീട് SQL ലേക്ക് മാറ്റാം)
products = [
    {"id": 1, "name": "Royal Wedding Silk", "price": "24,500", "img": "saree1.jpg", "cat": "Bridal"},
    {"id": 2, "name": "Golden Kasavu", "price": "8,900", "img": "saree2.jpg", "cat": "Traditional"},
    # ഇങ്ങനെയുള്ള 100 കണക്കിന് ഐറ്റംസ് ഇവിടെ ആഡ് ചെയ്യാം
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shop')
def shop():
    return render_template('shop.html', products=products)

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['user'] = request.form['username']
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)
