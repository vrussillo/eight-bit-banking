from operator import add
import os
from flask import Flask, render_template, session, redirect, flash, g, request
# from flask_debugtoolbar import DebugToolbarExtension
from forms import RegisterForm, LoginForm, AddCrypto, UserEditForm
from models import connect_db, db, User, Inventory, Crypto, SQLAlchemy
from sqlalchemy.exc import IntegrityError
from currencies import curr_logos
from coinblibapi import coin_id, value_list, key_list



CURR_USER_KEY = "user_id"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','postgresql:///eight_bit_banking_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get ('SECRET_KEY', 'billybobthorton1')
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# debug = DebugToolbarExtension(app)


connect_db(app)
# db.drop_all()
# db.create_all()


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


@app.route('/')
@app.route('/home')
@app.route('/index')
def index():
    """Return homepage."""
    user = g.user
    return render_template("index.html", user=user)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user: produce form & handle form submission."""

    form = RegisterForm()

    if form.validate_on_submit():
        name = form.username.data
        pwd = form.password.data
        email = form.email.data

        user = User.register(name, email, pwd)
        
        db.session.add(user)
        
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username Taken. Please Pick Another')
            
            return render_template("register.html", form=form)
        session["user_id"] = user.id

        # on successful login, redirect to inventory page
        return redirect(f"/inventory/{user.id}")

    else:
        return render_template("register.html", form=form)


@app.route('/addcrypto', methods=["GET", "POST"])
def add_crypto():
    """add crypto to inventory"""
    inventory = Inventory.query.all()
    user = User.query.all()

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    form = AddCrypto()

    if form.validate_on_submit():
        crypto = Crypto(crypt_name=form.type.data, amount=form.amount.data)
        g.user.cryptos.append(crypto)
        db.session.commit()
        user_id = session["user_id"]
        inv_id = Inventory(user_id=user_id, crypt_id=crypto.id, amount=crypto.amount)
        db.session.add(inv_id)
        db.session.commit()
        return redirect(f"/inventory/{g.user.id}")

    return render_template("add_crypto.html", inventory=inventory, user=user, form=form)


@app.route('/inventory/<int:user_id>', methods=["GET"])
def usr_inventory(user_id):
    """Return user inventory."""
    user = User.query.get_or_404(user_id)

    cryptos = (Crypto
                .query
                .filter(Crypto.user_id == user_id)
                .all())
    amount = Inventory.amount
    inventory = (Inventory
                .query
                .filter(Inventory.amount == amount)
                .all())
    if user_id != g.user.id:
        """keep user from accessing other user's inventory"""
        return redirect("/404")
    
    return render_template("inventory.html", user=user, cryptos=cryptos, inventory=inventory, curr_logos=curr_logos)


@app.route('/show_crypto/<int:crypt_id>')
def crypto_info(crypt_id):
    user_id = g.user.id
    
    crypto = Crypto.query.get_or_404(crypt_id)

    cryptos = (Crypto
                .query
                .filter(Crypto.id == crypt_id)
                .all())

                
    
    # for currency in crypto_currencies.currency:
    #     print(currency)

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    return render_template("show_crypto.html", crypto=crypto, user_id=user_id, curr_logos=curr_logos, cryptos=cryptos, coin_id=coin_id, value_list=value_list, key_list=key_list)


@app.route('/inventory/<int:crypt_id>/delete', methods=["POST"])
def delete_crypto(crypt_id):
    """Delete a message."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    crypto = Crypto.query.get_or_404(crypt_id)
    db.session.delete(crypto)
    db.session.commit()
    flash('Item deleted.')

    return redirect(f"/inventory/{g.user.id}")


@app.route('/account/<int:user_id>', methods=["GET", "POST"])
def usr_account(user_id):
    """user account settings"""
    

    if "user_id" not in session:
        flash("You must be logged in to view!")
        return redirect("/")

    if user_id != g.user.id:
        """keep user from accessing other user's inventory"""
        return redirect("/404")
    
    cryptos = (Crypto
                .query
                .filter(Crypto.user_id == user_id)
                .all())

    user = g.user

    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            user.username = form.username.data
            user.email = form.email.data
            user.image_url = form.image_url.data or "static/images/default-propic.png"
            

            db.session.commit()
            return redirect(f"/account/{user.id}")

        flash("Wrong password, please try again.", 'danger')

    return render_template('account.html', form=form, user=user, user_id=user.id, cryptos=cryptos)


@app.route('/account/<int:user_id>/delete', methods=["POST"])
def delete_user(user_id):
    """Delete user."""

    user = User.query.get_or_404(user_id)

    do_logout()
    
    db.session.delete(user)
    db.session.commit()
    

    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Produce login form or handle login."""
    
    
    form = LoginForm()

    if form.validate_on_submit():
        name = form.username.data
        pwd = form.password.data

        # authenticate will return a user or False
        user = User.authenticate(name, pwd)

        if user:
            session["user_id"] = user.id  # keep logged in
            return redirect(f"/inventory/{user.id}")

        else:
            form.username.errors = ["Incorrect Password"]

    return render_template("login.html", form=form)
# end-login


@app.route("/logout")
def logout():
    """Logs user out and redirects to homepage."""

    session.pop("user_id")
    return redirect("/")


@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404.html'), 404