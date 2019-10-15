from django.http import HttpResponse
from django.http import JsonResponse

from hashlib import md5

import requests
import os
import smtplib

from threading import Thread

from firstapp.models import Submit, Status

smtp_server = ''
port = ''
login = ''
password = ''


def submit(request):
    if request.method == "POST":
        new_object = Object(request)
        hash_thread = Thread(target=new_object.md5_hash)
        hash_thread.start()
        return JsonResponse({'id':f'{new_object.uuid}'})
    else:
        return HttpResponse(status=400)

def check(request):
    if request.method == "GET":
        task = Task(request)
        if task.uuid:
            status = task.get()
            print(status)
            if isinstance(status, int):
                return HttpResponse(status=status)
            return JsonResponse(status)
        else:
            return HttpResponse(status=404)
    else:
        return HttpResponse(status=400)

class Task:
    __slots__=["uuid", "status", "hash"]
    def __init__(self, request):
        self.uuid = request.GET.get("id")

    def get(self):
        try:
            if len(self.uuid)>36:
                return 400
            task = Status.objects.get(uuid=f'{self.uuid}')
            self.status = task.status
            self.hash = task.hash
            if self.hash:
                return {'id':f'{self.uuid}', 'status':f'{self.status}', 'MD5 Hash':f'{self.hash}'}
            else:
                return {'id': f'{self.uuid}', 'status': f'{self.status}'}
        except Status.DoesNotExist:
            return 404


class Object:
    __slots__ = ["email", "url", "uuid"]
    def __init__(self, request):
        self.email = request.GET.get("email", "")
        self.url = request.GET.get("url")
        print(self.url)
        if self.url:
            new_submit = Submit(url=self.url, email=self.email)
            self.uuid = new_submit.uuid
            new_submit.save()
            status = Status(uuid=self.uuid,status="Running")
            status.save()

    def md5_hash(self):
        task = Status.objects.get(uuid=self.uuid)
        print('Starting download file')
        try:
            new_file = requests.get(f'{self.url}')
        except:
            print('Connection Failed')
            task.status = "Error. Connection Failed"
            task.save()
        else:
            temp_file = open(f'{self.uuid}_temp_file', 'wb')
            temp_file.write(new_file.content)
            print('Successfully')
            temp_file.close()
            print('Open file')

            with open(f'{self.uuid}_temp_file', 'rb') as file:
                hash = md5()
                data = file.read()
                if data:
                    print("Start MD5 algoritm")
                    hash.update(data)
                    file.close()

                    task.hash = f'{hash.hexdigest()}'
                    task.status = 'Done'
                    task.save()
                    print('Success')
                    print('Delete temp file')
                    os.remove(f"{self.uuid}_temp_file")
                    print('Complete')
                    self.send_mail(task.hash)


    def send_mail(self, hash):
        smtp = smtplib.SMTP(smtp_server, port)
        code = smtp.starttls()
        print(code)
        if code[0]==220:
            try:
                smtp.login(login, password)
            except:
                print("Incorrect login or password")
            else:
                smtp.sendmail(login, f"{self.email}",f"Operation with ID: {self.uuid} successfully complete!\nURL: {self.url}\nMD5 Hash: {hash}")
                smtp.quit()
        else:
            print('SMTP Connection failed')


