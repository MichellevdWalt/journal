from collections import OrderedDict
import datetime
from flask import (Flask, g, render_template, flash, redirect, url_for,
                  abort)
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user,
                             login_required, current_user)

import forms
import models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'rplwco4!lmakdo03849!_ksdjfnbfihf>ksjdjdisj!'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.user_id == userid)
    except models.DoesNotExist:
        return None


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        models.User.create_user(
            username=form.username.data,
            password=form.password.data
        )
        flash("Registration successful!", "success")
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.username == form.username.data)
        except models.DoesNotExist:
            flash("Your email or password doesn't match!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in!", "success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password doesn't match!", "error")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "success")
    return redirect(url_for('index'))

@app.route('/', methods=('GET', 'POST'))
def index():
    return redirect(url_for('entries'))

@app.route('/entries', methods=('GET', 'POST'))
@login_required
def entries():
    journal_entries = models.Journal.select().where(
        models.Journal.user_id == current_user.user_id 
    ).limit(100)
    return render_template('index.html', journal_entries = journal_entries)

@app.route('/entries/new', methods=('GET', 'POST'))
def new_entry():
    form = forms.NewEntryForm()
    if form.validate_on_submit():
        models.Journal.create(
            title = form.title.data,
            date = datetime.datetime.strptime(form.date.data, '%d/%m/%Y'),
            time_spent = form.time_spent.data,
            learnt = form.learnt.data.strip(),
            resources = form.resources.data.strip(),
            user_id = current_user.user_id
        )
        flash("Entry added.", "success")
        return redirect(url_for('entries'))
    return render_template('new.html', form=form)

@app.route('/entries/<int:entry_id>')
def entry_detail(entry_id):
    try:
        entry = models.Journal.select().where(
            models.Journal.id == entry_id
            ).get()
    except models.DoesNotExist:
        abort(404)

    if entry.user_id != current_user.user_id:
        abort(401)
    
    
    if "\n" in entry.resources:
        resources = entry.resources.split("\n") 
    else:
        resources = entry.resources.split(",")

    return render_template("detail.html", entry=entry, resources=resources)
    

@app.route('/entries/<int:entry_id>/edit', methods=('GET', 'POST'))
def entry_edit(entry_id):
    try:
        entry = models.Journal.select().where(
            models.Journal.id == entry_id
        ).get()
    except models.DoesNotExist:
        abort(404)

    if entry.user_id != current_user.user_id:
        abort(401)
        
    form = forms.NewEntryForm(title = entry.title, date= datetime.datetime.strftime(entry.date, '%d/%m/%Y'), time_spent = entry.time_spent, learnt = entry.learnt, resources = entry.resources)
    if form.validate_on_submit():
        journal_update = models.Journal.update(
            title = form.title.data,
            date = datetime.datetime.strptime(form.date.data, '%d/%m/%Y'),
            time_spent = form.time_spent.data,
            learnt = form.learnt.data.strip(),
            resources = form.resources.data.strip()
        ).where(models.Journal.id == entry_id)
        journal_update.execute()
        flash("Entry updated.", "success")
        return redirect(url_for('entries'))
    return render_template('edit.html', entry=entry, form = form)


@app.route('/entries/<int:entry_id>/confirm_delete', methods=('GET', 'POST'))
def entry_confirm_delete(entry_id):
    entry = models.Journal.select().where(models.Journal.id == entry_id).get()
    return render_template('delete.html', entry=entry)

@app.route('/entries/<int:entry_id>/delete', methods=('GET', 'POST'))
def entry_delete(entry_id):
    entry = models.Journal.select().where(models.Journal.id == entry_id).get()
    delete_final = models.Journal.delete().where(models.Journal.id == entry_id)
    delete_final.execute()
    flash("Entry Deleted", "success")
    return redirect(url_for('entries'))


if __name__ == '__main__':
    models.initialize()
    try:
        models.User.get(models.User.user_id == "1")
    except models.DoesNotExist:
        models.User.create_user(
            username = "Michelle",
            password = "password"
        )

    try:
        models.Journal.get(models.Journal.title == "Welcome")
    except models.DoesNotExist:
        models.Journal.create_journal_entry(
            title ='Welcome',
            time_spent = 'Add the time you spent here in',
            learnt ='Add everything you learnt here',
            resources= 'Add all your resources here\nSeparated by a comma or\nline break',
            user = '1'
        )
    
    app.run(debug=DEBUG, host=HOST, port=PORT)