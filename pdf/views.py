from __future__ import print_function
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect, Http404, FileResponse
from django.contrib.auth import authenticate, login, logout
from django.db.models import Value, Count, CharField
from django.core.files.storage import FileSystemStorage
from .models import User_profile
from datetime import datetime 
from tzlocal import get_localzone

from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
from .forms import PDFMergeForm, PDFSplitForm, PDFDeleteForm

import os
import io
from zipfile import ZipFile
from apiclient.discovery import build
from google.oauth2 import service_account
from oauth2client import file, client, tools

from httplib2 import Http
from . import auth
from users.facadeGoogleDrive import GoogleDrive

# Create your views here.
def index(request):
    return render(request, "pdf/upload.html")


def upload(request ,name , file_path , mimetype):
    GoogleDrive().upload(request,name, file_path, mimetype)

def download(request , file_id , file_name , mimeType) :
    return GoogleDrive().download(file_id, file_name, mimeType)

def get_user_history(folder_id) :
    return GoogleDrive().get_user_history(folder_id)

def merge(request):
    if request.method == 'POST':
        form = PDFMergeForm(request.POST, request.FILES)
        if form.is_valid():
            # get file input from merge form
            file1 = form.cleaned_data['file1']
            file2 = form.cleaned_data['file2']

            # make sure that both input files is pdf
            if ((os.path.splitext(str(file1))[1] != '.pdf') or (os.path.splitext(str(file2))[1] != '.pdf')):
                return render(request, 'pdf/pdf_split.html', {'form':form})

            # merge two file
            pdfMerge = PdfFileMerger()
            pdfMerge.append(PdfFileReader(file1))
            pdfMerge.append(PdfFileReader(file2))

            # write merged file
            pdfMerge.write('merged_file.pdf')

            # output merged file
            response = FileResponse(open('merged_file.pdf', 'rb'))
            response['content_type'] = "application/pdf"
            response['Content-Disposition'] = 'attachment;filename="merged_file.pdf"'
            
            # check if user is not anonymous (authenticated user)
            # upload processed file to google drive
            if not request.user.is_anonymous:
                date_time = datetime.fromtimestamp(datetime.now().timestamp(),get_localzone()).strftime("%d/%m/%Y %H:%M:%S")
                upload(request,"merged file {}.pdf".format(date_time) , "merged_file.pdf" , "pdf")

            # remove processed file
            os.remove('merged_file.pdf')

            return response
        else:
            form = PDFMergeForm()
    else:
        form = PDFMergeForm()

    return render(request, 'pdf/pdf_merge.html', {'form':form})

def split(request):
    if request.method == 'POST':
        form = PDFSplitForm(request.POST, request.FILES)
        if form.is_valid():
            # get file input from split form
            inputFile = form.cleaned_data['file1']
            pageNum = form.cleaned_data['pageNum']

            # make sure that input file is pdf
            if (os.path.splitext(str(inputFile))[1] != '.pdf'):
                return render(request, 'pdf/pdf_split.html', {'form':form})

            # read input pdf
            inputPDF = PdfFileReader(inputFile)
            outputPDF1 = PdfFileWriter()
            outputPDF2 = PdfFileWriter()

            # make sure that page number is valid
            if ((int(pageNum) <= 0) or (int(pageNum) > inputPDF.getNumPages()) or (inputPDF.getNumPages() == 1)):
                return render(request, 'pdf/pdf_split.html', {
                    'message': 'Invalid',
                    'form': form,
                })

            # split first half of the pdf from 0 to page number
            for i in range(pageNum):
                outputPDF1.addPage(inputPDF.getPage(i))
                with open('splited_file_1.pdf', 'wb') as outfile:
                    outputPDF1.write(outfile)

            # split second half of the pdf from (page number+1) to last page
            for i in range(pageNum, inputPDF.getNumPages()):
                outputPDF2.addPage(inputPDF.getPage(i))
                with open('splited_file_2.pdf', 'wb') as outfile:
                    outputPDF2.write(outfile)

            # zip two file for output
            zf = ZipFile('splited_files.zip', "w")
            zf.write('splited_file_1.pdf', 'splited_file_1.pdf')
            zf.write('splited_file_2.pdf', 'splited_file_2.pdf')
            zf.close()

            # output splited file
            response = FileResponse(open('splited_files.zip', 'rb'))
            response['content_type'] = "application/pdf"
            response['Content-Disposition'] = 'attachment;filename="splited_files.zip"'

            # check if user is not anonymous (authenticated user)
            # upload processed file to google drive
            if not request.user.is_anonymous:
                date_time = datetime.fromtimestamp(datetime.now().timestamp(),get_localzone()).strftime("%d/%m/%Y %H:%M:%S")
                upload(request,"splited file {}.zip".format(date_time) , "splited_files.zip" , "zip")
                
            # remove processed file
            os.remove('splited_files.zip')
            os.remove('splited_file_1.pdf')
            os.remove('splited_file_2.pdf')

            return response

        else:
            form = PDFSplitForm()
    else:
        form = PDFSplitForm()

    return render(request, 'pdf/pdf_split.html', {'form':form})

def delete(request):
    if request.method == 'POST':
        form = PDFDeleteForm(request.POST, request.FILES)
        if form.is_valid():
            # get file input from delete form
            inputFile = form.cleaned_data['file1']

            # make sure that input file is pdf
            if (os.path.splitext(str(inputFile))[1] != '.pdf'):
                return render(request, 'pdf/pdf_split.html', {'form':form})

            # read input pdf
            inputPDF = PdfFileReader(inputFile)
            outputPDF = PdfFileWriter()
            
            # get the correct page(s) to delete
            pageNum = form.cleaned_data['pageNum'].replace(" ", "").split(',')
            pageToDeleteDup = []
            for page in pageNum:
                pageInt = [int(i) for i in page.split('-')]
                if (len(pageInt) == 2):
                    for i in range(pageInt[0], pageInt[-1] + 1):
                        pageToDeleteDup += [i]
                else:
                    pageToDeleteDup += pageInt

            pageToDelete = []
            # delete duplication page number in list
            for num in pageToDeleteDup:
                if num not in pageToDelete:
                    pageToDelete.append(num)


            # make sure that page number is valid
            if ((max(pageToDelete) > inputPDF.getNumPages()) or (min(pageToDelete) <= 0) or (inputPDF.getNumPages() == 1)):
                return render(request, 'pdf/pdf_delete.html', {
                    'message': 'Invalid',
                    'form': form,
                })

            # delete page(s)
            for i in range(inputPDF.getNumPages()):
                if (i + 1) not in pageToDelete:
                    outputPDF.addPage(inputPDF.getPage(i))
                    with open('deleted_file.pdf', 'wb') as outfile:
                        outputPDF.write(outfile)

            # output deleted file
            response = FileResponse(open('deleted_file.pdf', 'rb'))
            response['content_type'] = "application/pdf"
            response['Content-Disposition'] = 'attachment;filename="deleted_file.pdf"'

            # check if user is not anonymous (authenticated user)
            # upload processed file to google drive
            if not request.user.is_anonymous:
                date_time = datetime.fromtimestamp(datetime.now().timestamp(),get_localzone()).strftime("%d/%m/%Y %H:%M:%S")
                upload(request,"deleted file {}.pdf".format(date_time) , "deleted_file.pdf" , "pdf")
                
            # remove processed file
            os.remove('deleted_file.pdf')

            return response

        else:
            form = PDFDeleteForm()
    else:
        form = PDFDeleteForm()

    return render(request, 'pdf/pdf_delete.html', {'form':form})