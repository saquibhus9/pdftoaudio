from django.shortcuts import render, redirect
from django.contrib.sessions.models import Session
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import HttpResponse
from AppPdf.models import User_Details, Pdf_Details
from PyPDF2 import PdfReader
import gtts
from gtts import gTTS
import io
import os
from googletrans import Translator
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def home(request):
    return render(request, 'home.html', {})

def User_login(request):
    if request.method == 'POST':
        Username = request.POST['Username']
        password = request.POST['password']
        
        if User_Details.objects.filter(Username=Username, Password=password).exists():
            user = User_Details.objects.all().filter(Username=Username, Password=password)
            request.session['User_id'] = str(user[0].id)
            request.session['type_id'] = 'User'
            request.session['username'] = Username
            request.session['login'] = 'Yes'
            return redirect('/')
            
        else:
            messages.info(request,'Invalid Credentials')
            return redirect('/User_login/')
    else:
        return render(request, 'User_login.html', {})

def logout(request):
    Session.objects.all().delete()
    return redirect('/')

def PdfRead(request):
    if request.method == 'POST':
        pdf = request.FILES['FileName']
        name = str(pdf).replace('.pdf', '').replace(' ', '')
        lang = request.POST['Languages']

        pdf_file_obj = request.FILES['FileName'].read() 
        pdf_reader = PdfReader(io.BytesIO(pdf_file_obj))
        num_pages = len(pdf_reader.pages)
        content = ""

        for i in range(num_pages):
            page = pdf_reader.pages[i]
            content += page.extract_text()

        content = content.replace("\n", "").replace("  ", " ")

        translator = Translator()
        translated = translator.translate(content, dest=lang)
        translated_text = translated.text
        curr_date = datetime.datetime.now().strftime("%d-%m-%Y-%I-%M-%S")

        tts = gTTS(text=translated_text, slow=False, lang=lang)
        filename = os.path.join(BASE_DIR, 'media', 'Audio', f'{name}{curr_date}.mp3')
        tts.save(filename)

        pdf_detail = Pdf_Details(PdfName=pdf, Filename=f'/media/Audio/{name}{curr_date}.mp3', UserId=request.session['User_id'])
        pdf_detail.save()
        
        messages.info(request, 'Conversion Complete.')
        return redirect('/PdfRead/')
    else:
        return render(request, 'PdfRead.html', {})

def Register(request):
    if request.method == 'POST':
        first_name = request.POST['First_name']
        last_name = request.POST['Last_name']
        username = request.POST['Username']
        dob = request.POST['Dob']
        gender = request.POST['Gender']
        phone = request.POST['Phone']
        email = request.POST['Email']
        password = request.POST['Password']
        address = request.POST['Address']
        city = request.POST['City']
        state = request.POST['State']
        
        if User_Details.objects.filter(Username=username).exists():
            messages.info(request, 'Username taken')
            return redirect('/Register/')
        elif User_Details.objects.filter(Email=email).exists():
            messages.info(request, 'Email Id taken')
            return redirect('/Register/')
        else:  
            user_detail = User_Details(
                First_Name=first_name, Last_Name=last_name, Dob=dob, Gender=gender,
                Phone=phone, Email=email, Username=username, Password=password,
                Address=address, City=city, State=state)
            user_detail.save()
            messages.info(request, 'User Registered Successfully')
            return redirect('/Register/')
    else:
        return render(request, 'Register.html', {})

def ListenPdf(request):
    if request.method == 'POST':
        return redirect('/ListenPdf/')
    else:
        pdf_details = Pdf_Details.objects.filter(UserId=request.session['User_id'])
        return render(request, 'ListenPdf.html', {'Pdf_Det': pdf_details})

def test(request):
    if request.method == 'POST':
        return redirect('/test/')
    else:
        return render(request, 'PlayMusic.html', {})
