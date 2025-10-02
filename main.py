from flask import (
    Flask,
    render_template,
    request
)
import database_manager as dbHandler

app = Flask(__name__)

#--- --- --- --- --- --- --- --- --- --- --- ---
# Landing

@app.route('/', methods=['GET'])
def landing():
    return render_template('/landing.html')

#-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# Home

@app.route('/home', methods=['GET'])
def home():
    return render_template('/home.html')

#-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# Contact

@app.route('/contact_us', methods=['GET'])
def contact():
    return render_template('/contact.html')

#-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# About Us

@app.route('/about_us', methods=['GET'])
def about():
    return render_template('/about.html')

#-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# Donate

#-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# Sign Up/Sign In

@app.route('/signin', methods=['GET'])
def signin():
    return render_template('/signin.html')

#-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# Profile

@app.route('/profile', methods=['GET'])
def profile():
    return render_template('/profile.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
