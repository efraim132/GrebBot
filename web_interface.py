import os

from flask import Flask, render_template, send_from_directory

app = Flask(__name__,static_folder='templates/assets', static_url_path='/assets')



#Temporary
#TODO: Add in better routing support for the profile image of the website
@app.route('/ProfilePicture.png')
def profile_picture():
    return send_from_directory('templates', 'ProfilePicture.png')

@app.route('/')
def index():
    return render_template('index.html')

def run_web_interface():
    app.run(host='127.0.0.1', port=5000, use_reloader=False, threaded=True)


if __name__ == '__main__':
    app.run(debug=True)