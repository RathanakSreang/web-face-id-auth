from flask import Flask, render_template, redirect, url_for, session
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, UserMixin, current_user, login_user, \
                        login_required, logout_user
from flask_session import Session

import base64_2_image
import cv2
import numpy as np
import dlib
from imutils import face_utils
import imutils

print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()

app = Flask(__name__, static_url_path='', static_folder='static')
app.config['SECRET_KEY'] = 'secret!'
app.config['SESSION_TYPE'] = 'filesystem'
login = LoginManager(app)
Session(app)
socketio = SocketIO(app)


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
    return render_template('index.html', current_user = current_user)

@app.route('/login')
def login():
    if current_user.is_authenticated:
      return redirect(url_for('index'))

    # session['user_1'] = 'Rathanak'
    # login_user(User(1, 'Rathanak'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
  print('Logging out')
  logout_user()
  return redirect(url_for('index'))

# real time streaming
@socketio.on('stream')
def test_send_image(img):
    image = base64_2_image.data_uri_to_cv2_img(img)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = imutils.resize(gray, width=200)
    cv2.imwrite('testing.png', gray)
    rects = detector(gray, 0)
    print(len(rects))
    detectFace = []
    for rect in rects:
        (x,y,w,h) = face_utils.rect_to_bb(rect)
        detectFace.append({'x': x, 'y': y, 'w': w, 'h': h})
    emit('stream', {'img': img, 'detectFace': detectFace}, broadcast=True)

@socketio.on('connect')
def test_connect():
    emit('my response', {'data': 'Connected'})


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app, debug=True)
