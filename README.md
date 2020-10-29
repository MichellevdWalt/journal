******* TREEHOUSE PYTHON UNIT 5 PROJECT *********

Learning Journal.

To run this program:
    Run python3 app.py in the command line. 
    Runs on localhost:8000
    Please see requirements.txt for required packages.

NOTE: For testing I suggest registering a new user to get a feel for the full functionality, or you could log in with the mock-user: username = Michelle, Password = password. (This can be changed in app.py line 257 BEFORE first run, alternatively delete your instance of journal.db before re-running with new user in app.py line 257.)

This learning journal lets you register as a user and then add entries to the journal.

The program renders a registration or new entry form and then creates the necessary fields in the sqlite db.
All fields have the necessary validation.

The home page displays a short version of available entries and a detail page shows details of a specific entry. 
Details include a title, date, time spent, what you learned, resources to remember(These are converted to clickable hyperlinks that open in a new tab where applicable.) and tags.

It also has an edit and delete function, of which the buttons only display if the current user created
the entry. It also needs user validation, so even manual routing would end up at a 401.
If an entry does not exist, it routes the user to a 404 page.

Tags can be entered in the new entry form or edit form. 
These tags are clickable in the home page as well as the details page,
which routes the user to a page showing all entries with said tag.  

