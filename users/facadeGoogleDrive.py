from pdf import auth
from apiclient.discovery import build
from httplib2 import Http

from django.http import FileResponse
from django.contrib.auth.models import User
from pdf.models import User_profile
from apiclient.http import MediaFileUpload , MediaIoBaseDownload

import io
import os

class GoogleDrive :
    def __init__(self) :
        self.SCOPES =  'https://www.googleapis.com/auth/drive'
        self.CLIENT_SECRET_FILE = "client_secret.json"
        self.APPLICATION_NAME = "project_cn331"
        self.authInst = auth.auth(self.SCOPES, self.CLIENT_SECRET_FILE, self.APPLICATION_NAME)
        self.creds = self.authInst.getCredentials()
        self.http = self.creds.authorize(Http())
        self.drive_service = build('drive', 'v3', http = self.http)

    def create_folder(self,user) :
        file_metadata = {
                'name': user.username,
                'mimeType': 'application/vnd.google-apps.folder'
            }
        file = self.drive_service.files().create(body=file_metadata,fields='id').execute()
        user_profile = User_profile(ezpdf_user = user , folder_id = file.get('id'))
        user_profile.save()

    def upload(self,request , name , file_path , mimetype):
        file_metadata = {
            'name': name,
            'parents': [User_profile.objects.get(ezpdf_user = request.user).folder_id]
            }
        media = MediaFileUpload(file_path, mimetype=('application/' + mimetype) , resumable = True)
        file = self.drive_service.files().create(body=file_metadata,media_body=media,fields='id')

        #wait for upload file
        response = False
        while response is False:
            response = file.next_chunk()

    def download(self , file_id , file_name , mimeType) :
        file = self.drive_service.files().get_media(fileId=file_id).execute()
        fh = io.BytesIO(file)

        response = FileResponse(fh)
        response['content_type'] = "application/" + mimeType
        response['Content-Disposition'] = 'attachment;filename="{}"'.format(file_name)
        return response

    def get_user_history(self,folder_id) :
        file_history = [[]]
        results = self.drive_service.files().list(q="'{}' in parents and trashed = false".format(folder_id),fields="nextPageToken, files(id, name)").execute()
        fh = results.get('files', [])
        if fh:
            for file in fh:
                file_history[len(file_history)- 1].append(file.get('id'))
                file_history[len(file_history) - 1].append(file.get('name'))
                file_history[len(file_history) - 1].append(os.path.splitext(file.get('name'))[1])
                file_history.append([])

        file_history.remove([])
        return file_history