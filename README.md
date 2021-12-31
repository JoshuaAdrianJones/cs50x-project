# File share web app

#### Video Demo: https://youtu.be/kBdRuDoL9eU

#### Description:

Allow users to upload files and download them, and also make files available for other users to download.

This app solves a problem I have at work, we use language translators who work with .xml files to share and load documents into their language translation software.

Often this process involves sending emails with attachments back and forth to manage the translation process and recieve the files.

With this app a user could upload a file for translation and add a translator to the file so they can download it, then when their version in the translated language is complete,
the translator can upload their file and add the original work requester to the file so they can download the finished translation file.

This was a Flask + SQLITE3 app that allowed for:

- registering users
- login of users
- users can upload files
- users can download files
- users can delete files
- users can add other users to files so they can see the same file in their own dashboard - this is how file sharing can be done!

My database had 3 tables:

- a table for users to track their login details
- a table for files to track file info and storage location etc. to serve the file to be downloaded
- a table for file access this file has two foreign keys - file_id and user_id to be able to link the other two tables
- in file access each record is a pair of file_id and user_id so if you add a record then that file becomes visible to the user's dashboard.

I used a local folder as storage for the actual files and the database held links to the filepath.

To serve the files using a download button html form I used Flasks send_from_directory function.

# cs50x project

## flask app to upload and download files

## to setup

### to create a virtual environment

`$ python3 -m venv env`

### to install from requirements.txt

`$ pip install -r requirements.txt`

### environment

## to run

terminal commands:

`export FLASK_APP=app.py`

`export FLASK_ENV=development`

`flask run`

### Usage

- users can register an account
- login
- logout
- upload a file
- view and download available files
- add another user to be able to view the files
- delete a file

## Versioning

I used git / github for version control and had a main and dev branch set up.

## Authors

- Joshua Jones https://github.com/JoshuaAdrianJones

## License

This project is licensed under the MIT License
