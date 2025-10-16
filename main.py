from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_bootstrap import Bootstrap4
from flask_wtf import FlaskForm
import phonenumbers
from wtforms import BooleanField, StringField, PasswordField, SubmitField, SelectField, EmailField, DateField
from wtforms.fields.numeric import FloatField, IntegerField
from wtforms.validators import InputRequired, length, ValidationError, DataRequired, EqualTo, Optional, Email
from flask_bcrypt import Bcrypt
import database_manager as dbHandler
import sqlite3
import datetime
database = "databases/data_source.db"


def GetDB():
    con = sqlite3.connect(database)
    cur = con.cursor()
    return con, cur

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ithinkthiskeepsthecookies'
Bootstrap4(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

def loginrequired():
    if 'id' not in session:
        if request.referrer:
            return redirect(request.referrer)
        return redirect("/login")

@login_manager.user_loader
def load_user(user_id):
    con, cur = GetDB()
    account = cur.execute("SELECT [Email], [Phone Number] FROM Users WHERE ID=%s" % int(user_id)).fetchone()
    if account[0] is None:
        account.append(account[1])
    else:
        account.append(account[0])
    con.close()
    return account


class RequiredIf(InputRequired):

    def __init__(self, other_field_name, message=None, *args, **kwargs):
        self.other_field_name = other_field_name
        self.message = message
    def __call__(self, form, field):
        other_field = form[self.other_field_name]
        if other_field is None:
            raise Exception('No field named "%s" in form' % self.other_field_name)
        if bool(other_field.data):
            super(RequiredIf, self).__call__(form, field)
        else:
            Optional().__call__(form, field)

class LogInForm(FlaskForm):
    required = StringField(validators=[InputRequired()], render_kw={"placeholder": "Enter your email or phone number"})
    password = PasswordField(validators=[InputRequired()], render_kw={"placeholder": "Enter your password"})
    submit = SubmitField("Log In")

class RegisterForm(FlaskForm):
    first_name = StringField(validators=[InputRequired()], render_kw={"placeholder": "Enter first name"})
    last_name = StringField(validators=[Optional()], render_kw={"placeholder": "Enter last name"})
    password = PasswordField(validators=[InputRequired(), EqualTo('confirm', message='Passwords must match'), length(min=8, max=20, message='Password must be between 8-20 characters long.')], render_kw={"placeholder": "Enter password"})
    confirm = PasswordField(validators=[InputRequired(), length(min=8, max=20, message='Password must be between 8-20 characters long.')], render_kw={"placeholder": "Repeat password"})
    email = EmailField(validators=[RequiredIf("phone"), Email(message='Please enter a valid email.', check_deliverability=True)], render_kw={"placeholder": "Enter email"})
    phone = StringField(validators=[RequiredIf("email")], render_kw={"placeholder": "Enter phone number (e.g. +01 234 567 890)"})
    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError("Invalid Phone Number")
    city = StringField(validators=[InputRequired()], render_kw={"placeholder": "Enter city"})
    suburb = StringField(validators=[Optional()], render_kw={"placeholder": "Enter suburb"})
    donations = StringField(validators=[Optional()], render_kw={"placeholder": "Enter possible donations"})
    skills = StringField(validators=[Optional()], render_kw={"placeholder": "Enter skills"})
    struggling = BooleanField(validators=[])
    submit = SubmitField("Register")

    def validate_username(self, email, phone):
        con, cur = GetDB()
        existing_account = cur.execute("SELECT [Email], [Phone] FROM Users WHERE Email=%s OR Phone=%s" % (email, phone))
        con.close()
        if existing_account:
            raise ValidationError("The email or phone number already exists. Log in or use a different email or phone number.")

class UpdateAccForm(FlaskForm):
    first_name = StringField(validators=[])
    last_name = StringField(validators=[])
    current_password = PasswordField(validators=[])
    new_password = PasswordField(validators=[])
    def validate_password(self, current_password, new_password):
        user = session['user']
        if not bcrypt.check_password_hash(user[3], current_password.data):
            raise ValidationError("Incorrect Password")
        if current_password.length != 0 and new_password.length != 0:
            if current_password.data.length >= 8 and current_password.data.length <= 20:
                if new_password.data.length >= 8 and current_password.data.length <= 20:
                    return;
            raise ValidationError("Password must be between 8-20 characters long.")
    email = EmailField(validators=[Optional(), Email(message='Use a valid email.', check_deliverability=True)])
    phone = StringField(validators=[Optional()])
    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError("Invalid Phone Number")
    city = StringField(validators=[])
    suburb = StringField(validators=[])
    donations = StringField(validators=[])
    skills = StringField(validators=[])

    def validate_username(self, email, phone):
        con, cur = GetDB()
        existing_account = cur.execute("SELECT [Email], [Phone] FROM Users WHERE Email=%s OR Phone=%s" % (email, phone))
        con.close()
        if existing_account:
            raise ValidationError("The email or phone number already exists.")
    submit = SubmitField("Update Details")

class DonateForm(FlaskForm):
    item = StringField(validators=[InputRequired()], render_kw={"placeholder": "e.g. Canned Peach Slices"})
    dropoff = StringField(validators=[InputRequired()], render_kw={"placeholder": "Enter a nearby location"})
    date = DateField(validators=[InputRequired()])
    def validate_date(form, field):
        if field.data < datetime.time.today():
            raise ValidationError("The date cannot be in the past.")
    submit = SubmitField("Submit")



#--- --- --- --- --- --- --- --- --- --- --- ---
# Landing

@app.route('/', methods=['GET'])
def landing():
    if 'user' not in session:
        comms = ["loggedout"]
    else:
        comms = session['user']
    return render_template('/landing.html', comms=comms)

#-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# Home

@app.route('/home', methods=['GET','POST'])
def home():
    if 'user' in session:
        con, cur = GetDB()
        stat1 = cur.execute("SELECT COUNT([Donation ID]) FROM Donations WHERE [Donor ID]=%s AND [Successful?]='TRUE';" % (session['user'][0])).fetchone()[0]
        stat2 = cur.execute("SELECT COUNT([Donation ID]) FROM Donations WHERE [Recipient ID]=%s AND [Successful?]=TRUE;" % (session['user'][0])).fetchone()[0]
        stat3 = cur.execute("SELECT Item, COUNT(Item) AS count_item FROM Donations WHERE [Donor ID]=%s AND [Successful?]='TRUE' ORDER BY count_item DESC;" % (session['user'][0])).fetchone()[0]
        stat4 = cur.execute("SELECT COUNT(DISTINCT [Recipient ID]), COUNT([Donor ID]) FROM Donations WHERE [Donor ID]='%s' AND [Successful?]='TRUE';" % (session['user'][0])).fetchone()[0]
        if session['user'][9]:
            stat5 = session['user'][9]
        else:
            stat5 = "None";
        con.close()
        flaskcommunication = [session['user'], stat1, stat2, stat3, stat4, stat5]
        return render_template('/home.html', comms=flaskcommunication, user=session['user'])
    else:
        redirect(request.referrer)
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

@app.route('/donate', methods=['GET', 'POST'])
def donate():
    form = DonateForm()
    con, cur = GetDB()
    activedonations = cur.execute('SELECT * FROM Donatelist WHERE DonorID=%s ORDER BY Date ASC;' % (session['user'][0])).fetchall()
    if not activedonations:
        activedonations = []
    con.close()


    if form.validate_on_submit:
        if form.item.data:
            con, cur = GetDB()
            cur.execute("INSERT INTO Donatelist VALUES (?,?,?,?,?)",
                (
                    session['id'],
                    form.item.data,
                    form.dropoff.data,
                    form.date.data,
                    "Confirmed"
                ))
            con.commit()
            con.close()
            return redirect('home')
    return render_template('/donate.html', form=form, user=session['user'], activedonations=activedonations)

#-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# Log In

@app.route('/login', methods=['GET','POST'])
def login():
    form = LogInForm()
    if form.validate_on_submit:
        con, cur = GetDB()
        required = form.required.data
        user = None
        user = cur.execute("SELECT * FROM Users WHERE [Email]='%s' OR [Phone Number]='%s'" % (required, required)).fetchone()
        if user:
            if bcrypt.check_password_hash(user[3], form.password.data):
                login_user(user)
                session['id'] = user[0]
                if not user[4]:
                    user = user + (user[5],)
                else:
                    user = user + (user[4],)
                userlist = list(user)
                userlist[3] = userlist[3].decode("utf-8")
                session['user'] = userlist
                con.close()
                return redirect("/home")
        con.close()
    return render_template('/login.html', form=form)

#--- --- --- --- --- ---
# Log Out

@app.route('/logout', methods=['GET','POST'])
def logout():
    logout_user()
    session.pop('id', default=None)
    session.pop('user', default=None)
    return redirect('/')

#-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        con, cur = GetDB()
        userid = cur.execute("SELECT COUNT(*) FROM Users").fetchone()[0] + 1
        struggling = str(bool(form.struggling.data)).upper()
        cur.execute("INSERT INTO Users VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                userid,
                form.first_name.data,
                form.last_name.data,
                hashed_password,
                form.email.data,
                form.phone.data,
                form.city.data,
                form.suburb.data,
                form.donations.data,
                form.skills.data,
                struggling
            ))
        con.commit()
        con.close()
        return redirect("/login")
    return render_template('/register.html', form=form)

#-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# Profile

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    form = UpdateAccForm()
    user = list(session['user'])
    comms = [user] + ['placeholder value']
    if form.validate_on_submit():
        if form.first_name.data:
            user[1] = form.first_name.data
        if form.last_name.data:
            user[2] = form.last_name.data
        if form.new_password.data:
            user[3] = bcrypt.generate_password_hash(form.new_password.data)
        if form.email.data:
            user[4] = form.email.data
        if form.phone.data:
            user[5] = form.phone.data
        if form.city.data:
            user[6] = form.city.data
        if form.suburb.data:
            user[7] = form.suburb.data
        if form.donations.data:
            user[8] = form.donations.data
        if form.skills.data:
            user[9] = form.skills.data
        if user != list(session['user']):
            con, cur = GetDB()
            cur.execute('UPDATE Users SET [First Name]=? ,[Last Name (optional)]=?, [Password Hash]=?, Email=?, [Phone Number]=?, City=?, Suburb=?, [Potential Donations]=?, Skills=? WHERE ID=?', (user[1], user[2], user[3], user[4], user[5], user[6], user[7], user[8], user[9], user[0]))
            con.commit()
            con.close()
            if form.new_password.data:
                user[3] = user[3].decode("utf-8")
            comms = [user] + ['placeholder value']
            session['user'] = user
    return render_template('/profile.html', form=form, comms=comms)

#-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# Donation Process

@app.route('/the-donation-process', methods=['GET'])
def donationproc():
    return render_template('/donationproc.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)