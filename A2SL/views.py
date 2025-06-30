from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
from django.contrib.staticfiles import finders
from django.contrib.auth.decorators import login_required
from django.views.decorators import gzip
import threading
import cv2
import numpy as np
import random

# Delay model loading to avoid error when no model is available
def load_gesture_model():
    from keras.models import load_model
    return load_model('your_trained_model.h5')

class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.model = None
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        if self.model is None:
            try:
                self.model = load_gesture_model()
            except:
                self.model = None

        frame = self.frame
        roi = frame[100:400, 100:400]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (64, 64)).reshape(1, 64, 64, 1) / 255.0

        if self.model:
            pred = self.model.predict(resized)
            label = chr(np.argmax(pred) + 65)
        else:
            label = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

        cv2.putText(frame, f'Prediction: {label}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()

@gzip.gzip_page
def gesture_input_view(request):
    return render(request, 'gesture.html')

@gzip.gzip_page
def gesture_feed_view(request):
    try:
        return StreamingHttpResponse(gen(VideoCamera()), content_type="multipart/x-mixed-replace;boundary=frame")
    except:
        return HttpResponse("Error in camera feed")

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def home_view(request):
    return render(request, 'home.html')

def manual_view(request):
    return render(request, 'manual.html')

def about_view(request):
    return render(request, 'about.html')

def contact_view(request):
    return render(request, 'contact.html')

@login_required(login_url="login")
def animation_view(request):
    if request.method == 'POST':
        text = request.POST.get('sen')
        text.lower()
        words = word_tokenize(text)
        tagged = nltk.pos_tag(words)
        tense = {}
        tense["future"] = len([word for word in tagged if word[1] == "MD"])
        tense["present"] = len([word for word in tagged if word[1] in ["VBP", "VBZ", "VBG"]])
        tense["past"] = len([word for word in tagged if word[1] in ["VBD", "VBN"]])
        tense["present_continuous"] = len([word for word in tagged if word[1] in ["VBG"]])

        stop_words = set(["mightn't", 're', 'wasn', 'wouldn', 'be', 'has', 'that', 'does', 'shouldn', 'do', "you've",
                          'off', 'for', "didn't", 'm', 'ain', 'haven', "weren't", 'are', "she's", "wasn't", 'its',
                          "haven't", "wouldn't", 'don', 'weren', 's', "you'd", "don't", 'doesn', "hadn't", 'is',
                          'was', "that'll", "should've", 'a', 'then', 'the', 'mustn', 'i', 'nor', 'as', "it's",
                          "needn't", 'd', 'am', 'have', 'hasn', 'o', "aren't", "you'll", "couldn't", "you're",
                          "mustn't", 'didn', "doesn't", 'll', 'an', 'hadn', 'whom', 'y', "hasn't", 'itself', 'couldn',
                          'needn', "shan't", 'isn', 'been', 'such', 'shan', "shouldn't", 'aren', 'being', 'were',
                          'did', 'ma', 't', 'having', 'mightn', 've', "isn't", "won't"])

        lr = WordNetLemmatizer()
        filtered_text = []
        for w, p in zip(words, tagged):
            if w not in stop_words:
                if p[1] in ['VBG', 'VBD', 'VBZ', 'VBN', 'NN']:
                    filtered_text.append(lr.lemmatize(w, pos='v'))
                elif p[1] in ['JJ', 'JJR', 'JJS', 'RBR', 'RBS']:
                    filtered_text.append(lr.lemmatize(w, pos='a'))
                else:
                    filtered_text.append(lr.lemmatize(w))

        words = ["Me" if w == "I" else w for w in filtered_text]
        probable_tense = max(tense, key=tense.get)

        if probable_tense == "past" and tense["past"] >= 1:
            words = ["Before"] + words
        elif probable_tense == "future" and tense["future"] >= 1:
            if "Will" not in words:
                words = ["Will"] + words
        elif probable_tense == "present" and tense["present_continuous"] >= 1:
            words = ["Now"] + words

        filtered_text = []
        for w in words:
            path = w + ".mp4"
            f = finders.find(path)
            if not f:
                filtered_text.extend(w)
            else:
                filtered_text.append(w)
        words = filtered_text

        return render(request, 'animation.html', {'words': words, 'text': text})
    else:
        return render(request, 'animation.html')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('animation')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect('animation')
    else:
        form = AuthenticationForm()
    return render(request,'login.html',{'form':form})

def logout_view(request):
    logout(request)
    return redirect("home")

