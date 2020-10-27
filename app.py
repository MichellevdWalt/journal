from flask import (Flask, g, render_template, flash, redirect, url_for,
                  abort)
import forms
import models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'rplwco4!lmakdo03849!_ksdjfnbfihf>ksjdjdisj!'

@app.route('/', methods=('GET', 'POST'))
def index():
    return redirect(url_for('entries'))

@app.route('/entries', methods=('GET', 'POST'))
def entries():
    journal_entries = models.Journal.select().limit(100)
    return render_template('index.html', journal_entries = journal_entries)

@app.route('/entries/new', methods=('GET', 'POST'))
def new_entry():
    pass

@app.route('/entries/<int:entry_id>')
def entry_detail(entry_id):
    entry = models.Journal.select().where(
        models.Journal.id == entry_id
        ).get()
    print(entry)
    return render_template("detail.html", entry=entry)

    
    

@app.route('/entries/<id>/edit', methods=('GET', 'POST'))
def entry_edit():
    pass


@app.route('/entries/<id>/delete', methods=('GET', 'POST'))
def entry_delete():
    pass

if __name__ == '__main__':
    models.initialize()
    try:
        models.Journal.get(models.Journal.title == "Welcome")
    except models.DoesNotExist:
        models.Journal.create_journal_entry(
            title ='Welcome',
            time_spent = 'Add the time you spent here',
            learnt ='Add everything you learnt here',
            resources= 'Add all your resources here'
        )
    
    app.run(debug=DEBUG, host=HOST, port=PORT)