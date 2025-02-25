from tkinter import messagebox
from tkinter import *
from tkinter import simpledialog
import tkinter
from tkinter import filedialog
from tkinter.filedialog import askopenfilename
import matplotlib.pyplot as plt
import numpy as np
import joblib
from keras.models import load_model
from keras.preprocessing.image import img_to_array
import cv2
from keras.models import model_from_json
from keras.preprocessing import image
#from keras.optimizers import Adam
# from keras.utils import np_utils
from keras.preprocessing import image
import os
from numpy import dot
from numpy.linalg import norm
from keras.models import Sequential
from keras.layers import Dense, Conv2D, Dropout, Flatten, MaxPooling2D
import imutils
import nltk


main = tkinter.Tk()
main.title("Automating E-Government")
main.geometry("1300x1200")

global filename
global text_sentiment_model
EMOTIONS = ["angry","disgust","scared", "happy", "sad", "surprised","neutral"]
global face_detection
global image_sentiment_model
global digits_cnn_model

def digitModel():
    global digits_cnn_model
    with open('models/digits_cnn_model.json', "r") as json_file:
           loaded_model_json = json_file.read()
           digits_cnn_model = model_from_json(loaded_model_json)

    digits_cnn_model.load_weights("models/digits_cnn_weights.h5")
    digits_cnn_model._make_predict_function()   
    print(digits_cnn_model.summary())
    text.insert(END,'Digits based Deep Learning CNN Model generated\n')        
    
def sentimentModel():
    global text_sentiment_model
    global image_sentiment_model
    global face_detection
    text_sentiment_model = joblib.load('models/sentimentModel.pkl')
    text.insert(END,'Text based sentiment Deep Learning CNN Model generated\n')

    face_detection = cv2.CascadeClassifier('models/haarcascade_frontalface_default.xml')
    image_sentiment_model = load_model('models/_mini_XCEPTION.106-0.65.hdf5', compile=False)
    text.insert(END,'Image based sentiment Deep Learning CNN Model generated\n')
    print(image_sentiment_model.summary())
    
def digitRecognize():
    global filename
    filename = filedialog.askopenfilename(initialdir="testImages")
    pathlabel.config(text=filename)
    text.delete('1.0', END)
    text.insert(END,filename+" loaded\n");

    imagetest = image.load_img(filename, target_size = (28,28), grayscale=True)
    imagetest = image.img_to_array(imagetest)
    imagetest = np.expand_dims(imagetest, axis = 0)
    pred = digits_cnn_model.predict(imagetest.reshape(1, 28, 28, 1))
    predicted = str(pred.argmax())
    imagedisplay = cv2.imread(filename)
    orig = imagedisplay.copy()
    output = imutils.resize(orig, width=400)
    cv2.putText(output, "Digits Predicted As : "+predicted, (10, 25),  cv2.FONT_HERSHEY_SIMPLEX,0.7, (0, 255, 0), 2)
    cv2.imshow("Predicted Image Result", output)
    cv2.waitKey(0)


def opinion():
    user = simpledialog.askstring("Please enter your name", "Username")
    opinion = simpledialog.askstring("Government Service Opinion", "Please write your Opinion about government services & policies")
    f = open("Peoples_Opinion/opinion.txt", "a+")
    f.write(user+"#"+opinion+"\n")
    f.close()
    messagebox.showinfo("Thank you for your opinion", "Your opinion saved for reviews")


def stem(textmsg):
    stemmer = nltk.stem.PorterStemmer()
    textmsg_stem = ''
    textmsg = textmsg.strip("\n")
    words = textmsg.split(" ")
    words = [stemmer.stem(w) for w in words] 
    textmsg_stem = ' '.join(words)
    return textmsg_stem

def viewSentiment():
    text.delete('1.0', END)
    with open("Peoples_Opinion/opinion.txt", "r") as file:
        for line in file:
            line = line.strip('\n')
            line = line.strip()
            arr = line.split("#")
            text_processed = stem(arr[1])
            X =  [text_processed]
            sentiment = text_sentiment_model.predict(X)
            predicts = 'None'
            if sentiment[0] == 0:
                predicts = "Negative"
            if sentiment[0] == 1:
                predicts = "Positive"
            text.insert(END,"Username : "+arr[0]+"\n");
            text.insert(END,"Opinion  : "+arr[1]+" : Sentiment Detected As : "+predicts+"\n\n")
   
def uploadPhoto():
    filename = filedialog.askopenfilename(initialdir="expression_images_to_upload")
    user = simpledialog.askstring("Please enter your name", "Username")
    policy = simpledialog.askstring("Please enter Government Policy name related to Facial Expression", "Please enter Government Policy name related to Facial Expression")
    img = cv2.imread(filename)
    cv2.imwrite("sentimentImages/"+user+"-"+policy+".jpg",img);
    messagebox.showinfo("Your facial expression image accepted for reviews", "Your facial expression image accepted for reviews")

def photoSentiment():
    filename = 'sentimentImages'
    for root, dirs, files in os.walk(filename):
      for fdata in files:
          frame = cv2.imread(root+"/"+fdata)
          faces = face_detection.detectMultiScale(frame,scaleFactor=1.1,minNeighbors=5,minSize=(30,30),flags=cv2.CASCADE_SCALE_IMAGE)
          msg = ''
          if len(faces) > 0:
              faces = sorted(faces, reverse=True,key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))[0]
              (x, y, w, h) = faces
              cv2.rectangle(frame, (x,y), (x+w,y+h), (0,0,255), 2)
              temp = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
              roi = temp[y:y + h, x:x + w]
              roi = cv2.resize(roi, (48, 48))
              roi = roi.astype("float") / 255.0
              roi = img_to_array(roi)
              roi = np.expand_dims(roi, axis=0)
              preds = image_sentiment_model.predict(roi)[0]
              emotion_probability = np.max(preds)
              label = EMOTIONS[preds.argmax()]
              msg = "Sentiment detected as : "+label
              img_height, img_width = frame.shape[:2]
              cv2.putText(frame, msg, (50,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,255), 2)
              cv2.imshow(fdata,frame)
              messagebox.showinfo(fdata, "Sentiment predicted from Facial expression as : "+label)
              if cv2.waitKey(10) & 0xFF == ord('q'):
                  break
    cv2.waitKey(0)
    cv2.destroyAllWindows()                
    
    
font = ('times', 16, 'bold')
title = Label(main, text='Automating E-Government Services With Artificial Intelligence',anchor=W, justify=CENTER)
title.config(bg='LightSeaGreen', fg='white')  
title.config(font=font)           
title.config(height=3, width=130)       
title.place(x=0,y=5)


font1 = ('times', 14, 'bold')
digitButton = Button(main, text="Generate Hand Written Digits Recognition Deep Learning Model", command=digitModel)
digitButton.place(x=50,y=100)
digitButton.config(font=font1)  

pathlabel = Label(main)
pathlabel.config(bg='DarkOrchid', fg='white')  
pathlabel.config(font=font1)           
pathlabel.place(x=50,y=150)

sentimentButton = Button(main, text="Generate Text & Image Based Sentiment Detection Deep Learning Model", command=sentimentModel)
sentimentButton.place(x=50,y=200)
sentimentButton.config(font=font1)

recognizeButton = Button(main, text="Upload Test Image & Recognize Digit", command=digitRecognize)
recognizeButton.place(x=50,y=250)
recognizeButton.config(font=font1)

opinionButton = Button(main, text="Write Your Opinion About Government Policies", command=opinion)
opinionButton.place(x=50,y=300)
opinionButton.config(font=font1)

viewButton = Button(main, text="View Peoples Sentiments From Opinions", command=viewSentiment)
viewButton.place(x=50,y=350)
viewButton.config(font=font1)

photoButton = Button(main, text="Upload Your Face Expression Photo About Government Policies", command=uploadPhoto)
photoButton.place(x=50,y=400)
photoButton.config(font=font1)

photosentimentButton = Button(main, text="Detect Sentiments From Face Expression Photo", command=photoSentiment)
photosentimentButton.place(x=50,y=450)
photosentimentButton.config(font=font1)


font1 = ('times', 12, 'bold')
text=Text(main,height=15,width=75)
scroll=Scrollbar(text)
text.configure(yscrollcommand=scroll.set)
text.place(x=680,y=100)
text.config(font=font1)


main.config(bg='HotPink2')
main.mainloop()
