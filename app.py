from flask import Flask, render_template, redirect, url_for, session, request
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, UserMixin, current_user, login_user, \
                        login_required, logout_user
from flask_session import Session

import base64_2_image
import recognize_face

import cv2
import numpy as np
import dlib
from imutils import face_utils
import imutils

print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()

print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()

app = Flask(__name__, static_url_path='', static_folder='static')
app.config['SECRET_KEY'] = 'secret!'
app.config['SESSION_TYPE'] = 'filesystem'
login = LoginManager(app)
Session(app)
socketio = SocketIO(app)
recognizer = recognize_face.RecognizeFace()

class User(UserMixin, object):
    def __init__(self, id=None, name=''):
        self.id = id
        self.name = name

@login.user_loader
def load_user(id):
    try:
      name = session['user_' + id]
      return User(id, name)
    except:
      return None

@app.route('/')
def index():
    return render_template('index.html', user_name = current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'GET':
      return render_template('login.html')

    print(request.form)
    if request.form['auth_key'] == '1234567890':
      login_user(User(1, 'Rathanak'))
      session['user_1'] = 'Rathanak'
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    print('Logging out')
    logout_user()
    return redirect(url_for('index'))

# real time streaming
@socketio.on('stream')
def send_image(img):
    image = base64_2_image.data_uri_to_cv2_img(img)
    image = imutils.resize(image, width=200)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    rects = detector(gray, 0)
    rectFace = {}
    if len(rects) > 0:
        recognizer.AddImage(faceImage=image, gray=gray, rect=rects[0])
        (x,y,w,h) = face_utils.rect_to_bb(rects[0])
        rectFace['x'] = x
        rectFace['y'] = y
        rectFace['w'] = w
        rectFace['h'] = h

    emit('stream', {'img': img, 'rectFace': rectFace}, broadcast=True)

# real time streaming
@socketio.on('stream-end')
def send_image_end(img):
  emit('stream-end', {'endded': True}, broadcast=True)

@socketio.on('verify-user')
def verifyt_user(img):
  id, name, accouracy = recognizer.Recognize()
  recognizer.ClearFace()
  auth_key = ''
  if id is not None:
      auth_key = '1234567890'
  emit('verify-user', {'id': id, 'name': name, 'auth_key': auth_key,'accouracy': accouracy}, broadcast=True)

@socketio.on('connect')
def test_connect():
    emit('my response', {'data': 'Connected'})

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True)
