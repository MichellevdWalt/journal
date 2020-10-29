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
    """Login_manager's load_user"""
    try:
        return models.User.get(models.User.user_id == userid)
    except models.DoesNotExist:
        return None


@app.route('/register', methods=('GET', 'POST'))
def register():
    """Render registration form and handles submit"""
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
    """Renders login form and handles submit"""
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(
                models.User.username == form.username.data)
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
    """Logs out user"""
    logout_user()
    flash("Logged out successfully", "success")
    return redirect(url_for('index'))

@app.route('/', methods=('GET', 'POST'))
def index():
    """Redirects to /entries"""
    return redirect(url_for('entries'))

@app.route('/entries', methods=('GET', 'POST'))
def entries():
    """Renders page with simple view of all entries in db"""
    journal_entries = models.Journal.select().limit(100)
    tags = models.Tags.select()
    return render_template('index.html', 
                            journal_entries = journal_entries, 
                            tags = tags
    )

@app.route('/entries/new', methods=('GET', 'POST'))
@login_required
def new_entry():
    """Renders the new entry form and handles submit to db"""
    form = forms.NewEntryForm()
    if form.validate_on_submit():
        entry = models.Journal.create(
            title = form.title.data,
            date = datetime.datetime.strptime(form.date.data, 
                                              '%d/%m/%Y'),
            time_spent = form.time_spent.data,
            learnt = form.learnt.data.strip(),
            resources = form.resources.data.strip(),
            user_id = current_user.user_id,
            tags_str = form.tags.data
        )
        tag_list = form.tags.data.split(", ")
        for tag in tag_list:
            models.Tags.create(
                tag = tag,
                entry = entry
            )
        flash("Entry added.", "success")
        return redirect(url_for('entries'))
    return render_template('new.html', form=form)

@app.route('/entries/<int:entry_id>')
def entry_detail(entry_id):
    """Renders detailed page of single entry"""
    try:
        entry = models.Journal.select().where(
            models.Journal.id == entry_id
            ).get()
    except models.DoesNotExist:
        abort(404)
    
    if "\n" in entry.resources:
        resources = entry.resources.split("\n")
    else:
        resources = entry.resources.split(",")

    tags = models.Tags.select().where(
        models.Tags.entry_id == entry_id
    )
    if current_user.is_authenticated:
        if entry.user_id != current_user.user_id:
            access = False
        else:
            access = True
    else:
        access = False

    return render_template("detail.html", entry=entry, 
                            resources=resources, access=access, 
                            tags=tags)
    

@app.route('/entries/<int:entry_id>/edit', methods=('GET', 'POST'))
@login_required
def entry_edit(entry_id):
    """Renders populated entry form and handles db update"""
    try:
        entry = models.Journal.select().where(
            models.Journal.id == entry_id
        ).get()
    except models.DoesNotExist:
        abort(404)

    if entry.user_id != current_user.user_id:
        abort(401)

    form = forms.NewEntryForm(title = entry.title, 
                              date= datetime.datetime.strftime(entry.date, '%d/%m/%Y'), 
                              time_spent = entry.time_spent, 
                              learnt = entry.learnt, 
                              resources = entry.resources, 
                              tags = entry.tags_str
                             )
    if form.validate_on_submit():
        journal_update = models.Journal.update(
            title = form.title.data,
            date = datetime.datetime.strptime(form.date.data, '%d/%m/%Y'),
            time_spent = form.time_spent.data,
            learnt = form.learnt.data.strip(),
            resources = form.resources.data.strip(),
            tags_str = form.tags.data
        ).where(models.Journal.id == entry_id)
        journal_update.execute()

        #Clears tags to prevent doubles and deleted tags
        #from persisting in the db
        tags_delete = models.Tags.delete().where(
            models.Tags.entry_id == entry_id)
        tags_delete.execute()

        entry_updated = models.Journal.select().where(
            models.Journal.id == entry_id).get()

        tags_list = entry_updated.tags_str.split(", ")
        for tag in tags_list:
            models.Tags.create(
                tag = tag,
                entry = entry_id)
        flash("Entry updated.", "success")
        return redirect(url_for('entry_detail', entry_id=entry_id))
    return render_template('edit.html', entry=entry, form = form)


@app.route('/entries/<int:entry_id>/confirm_delete', methods=('GET', 'POST'))
@login_required
def entry_confirm_delete(entry_id):
    """Renders confirmation of deletion page"""
    try:
        entry = models.Journal.select().where(models.Journal.id == entry_id).get()
    except models.DoesNotExist:
        abort(404)

    if entry.user_id != current_user.user_id:
        abort(401)

    return render_template('delete.html', entry=entry)

@app.route('/entries/<int:entry_id>/delete', methods=('GET', 'POST'))
@login_required
def entry_delete(entry_id):
    """Handles permanent deletion of specific entry"""
    entry = models.Journal.select().where(
        models.Journal.id == entry_id).get()
    delete_final = models.Journal.delete().where(
        models.Journal.id == entry_id)
    delete_final.execute()
    flash("Entry Deleted", "success")
    return redirect(url_for('entries'))

@app.route('/entries/<tag>')
def entry_tags(tag):
    """Renders page matching chosen tag"""
    tags = models.Tags.select()
    tagged_entries = models.Journal.select().join(models.Tags).where(
        models.Tags.tag == tag)
    if tagged_entries.count() == 0:
        abort(404)
    else:
        return render_template('tags.html', 
                                tagged_entries=tagged_entries, 
                                tags=tags, 
                                tag=tag)
 

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
            resources= ('Add all your resources\n'
                        'and/or websites here\n'
                        'Separated by a comma or\n'
                        'line break'),
            user = '1',
            tags_str = "welcome, entry")

            entry = models.Journal.get(
                models.Journal.title == "Welcome")
            tag_list = entry.tags_str.split(", ")
            for tag in tag_list:
                models.Tags.create(
                    tag = tag,
                    entry = entry.id)
    
    app.run(debug=DEBUG, host=HOST, port=PORT)
