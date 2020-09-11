# Saving and loading model and weights
from tensorflow.keras.models import model_from_json
from tensorflow.keras.models import load_model
import tensorflow as tf
import numpy as np
import dlib
import cv2
from imutils.face_utils import FaceAligner

class RecognizeFace:
    def __init__(self):
        json_file = open('model.json', 'r')
        # load json and create model
        loaded_model_json = json_file.read()
        json_file.close()
        self.loaded_model = model_from_json(loaded_model_json)
        # load weights into new model
        self.loaded_model.load_weights("model.h5")
        # self.loaded_model._make_predict_function()
        tf.executing_eagerly()
        self.model_graph = tf.compat.v1.get_default_graph()
        print("Loaded model from disk")

        predictor = dlib.shape_predictor("model/shape_predictor_68_face_landmarks.dat")
        self.fa = FaceAligner(predictor, desiredFaceWidth=256)
        self.faces = []
        self.people = ['Rathanak', 'Unknown']

    def AddImage(self, faceImage, gray, rect):
      faceAligned = self.fa.align(faceImage, gray, rect)
      faceAligned = cv2.cvtColor(faceAligned, cv2.COLOR_BGR2GRAY)
      faceAligned = np.array(faceAligned)
      faceAligned = faceAligned.astype('float32')
      faceAligned /= 256
      faceAligned= np.expand_dims([faceAligned], axis=3)

      self.faces.append(faceAligned)

    def Recognize(self):
      if len(self.faces) == 0:
        return [None, 'Unknown', 1]
      result = [0, 0]
      for idx in np.random.randint(len(self.faces), size=5):
        self.loaded_model.run_eagerly = True
        Y_pred = self.loaded_model.predict(self.faces[idx])
        for index, value in enumerate(Y_pred[0]):
          print(self.people[index] + str(int(value * 100)) + '%')
          result[index] = result[index] + value
      # with self.model_graph.as_default():

      if result[0] > result[1]:
        return [1, 'Rathanak', str(int(result[0] *100 / 5)) + '%']
      else:
        return [None, 'Unknown', str(int(result[0] *100 / 5)) + '%']

    def ClearFace(self):
        self.faces = []
