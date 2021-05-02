from django.test import Client, TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Max
from PyPDF2 import PdfFileReader, PdfFileWriter
from zipfile import ZipFile
from diff_pdf_visually import pdfdiff
import io
import os
from pathlib import Path
# Create your tests here.

class PdfEditTest(TestCase):

    def setUp(self):
        # Create user
        User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='user1',
        )

    def test_merge_page(self):
        """Check that anonymous can access merge page"""

        response = self.client.get('/pdf/merge/')
        # Make sure that status code is 200
        self.assertEqual(response.status_code, 200)
        # Make sure that user access to the right page
        self.assertTemplateUsed(response, 'pdf/pdf_merge.html')

    def test_split_page(self):
        """Check that anonymous can access split page"""

        response = self.client.get('/pdf/split/')
        # Make sure that status code is 200
        self.assertEqual(response.status_code, 200)
        # Make sure that user access to the right page
        self.assertTemplateUsed(response, 'pdf/pdf_split.html')

    def test_delete_page(self):
        """Check that anonymous can access delete page"""

        response = self.client.get('/pdf/delete/')
        # Make sure that status code is 200
        self.assertEqual(response.status_code, 200)
        # Make sure that user access to the right page
        self.assertTemplateUsed(response, 'pdf/pdf_delete.html')
    
    def test_merge_anonymous_valid(self):
        """Check that anonymous can upload 2 pdf files and get the correct merged pdf file"""
        # Path for pdf file from local directory
        testDir = '/Users/palm/Data/University/3_1/CN340/Project/pdf_test/'

        # Open file from local directory 
        # Both files have 1 page
        openFile1 = open(testDir + 'dummy.pdf', 'rb')
        openFile2 = open(testDir + 'dummy-pdf_2.pdf', 'rb')
        
        response = self.client.post('/pdf/merge/', {
            'file1':openFile1, 
            'file2':openFile2,
        })

        # Make sure that status code is 200
        self.assertEqual(response.status_code, 200)
        
        # Make sure that response attached the right file
        self.assertEqual(response.get('Content-Disposition'), 'attachment;filename="merged_file.pdf"')

        # Read output file back from FileResponse
        content = list(response.streaming_content)
        bContent = b''.join(content)
        pdfFile = io.BytesIO(bContent)
        reader = PdfFileReader(pdfFile)

        # Both input pdfs have 1 page
        # Merged file should have 2 pages
        self.assertEqual(reader.getNumPages(), 2)

        # diff_pdf_visually lib needs the file to exist locally
        # Write the output file to local storage
        output = PdfFileWriter()
        for i in range(reader.getNumPages()):
            output.addPage(reader.getPage(i))
        outfile = open(testDir + 'test_merged_file.pdf', 'wb') 
        output.write(outfile)
        # Wait for file to finish writing
        outfile.close()
        
        # Make sure that output pdf have the correct result
        # using diff_pdf_visually lib
        # The lib take 2 parameters. that is path for both pdf file in local directory
        verFile = testDir + 'merged_file.pdf'
        verFile2 = testDir + 'test_merged_file.pdf'
        # The lib will return true if both pdf are the same
        self.assertTrue(pdfdiff(verFile, verFile2))

        # remove output file after finish testing
        os.remove(verFile2)
        
    def test_split_anonymous_valid(self):
        """Check that anonymous can upload pdf file, input page number and get the correct splited pdf files in zip format"""
        # Path for pdf file from local directory
        testDir = '/Users/palm/Data/University/3_1/CN340/Project/pdf_test/'

        # Open file from local directory 
        # Chosen PDF have 2 pages
        openFile = open(testDir + 'merged_file.pdf', 'rb')
        # Page number is 1
        # After split, first file should have 1st page and second file should have 2nd page
        inPageNum = 1

        response = self.client.post('/pdf/split/', {
            'file1':openFile, 
            'pageNum':inPageNum,
        })

        # Make sure that status code is 200
        self.assertEqual(response.status_code, 200)
        
        # Make sure that response attached the right file
        self.assertEqual(response.get('Content-Disposition'), 'attachment;filename="splited_files.zip"')

        # Read output file back from FileResponse
        content = list(response.streaming_content)
        bContent = b''.join(content)

        # Unzip file from FileResponse
        inZip = ZipFile(io.BytesIO(bContent))
        inZip.extractall()

        # Open both extracted file
        inPdf1 = open('splited_file_1.pdf', 'rb')
        inPdf2 = open('splited_file_2.pdf', 'rb')
        
        pdf1 = PdfFileReader(inPdf1)
        pdf2 = PdfFileReader(inPdf2)

        # Original file have 2 pages
        # Splited files should have 1 page for both file
        self.assertEqual(pdf1.getNumPages(), 1)
        self.assertEqual(pdf2.getNumPages(), 1)

        # diff_pdf_visually lib needs the file to exist locally
        # Write first file to local storage
        pdf1Output = PdfFileWriter()
        for i in range(pdf1.getNumPages()):
            pdf1Output.addPage(pdf1.getPage(i))
        outfile1 = open(testDir + 'test_splited_file_1.pdf', 'wb') 
        pdf1Output.write(outfile1)
        # Wait for file to finish writing
        outfile1.close()

        # Write second file to local storage
        pdf2Output = PdfFileWriter()
        for i in range(pdf2.getNumPages()):
            pdf2Output.addPage(pdf2.getPage(i))
        outfile2 = open(testDir + 'test_splited_file_2.pdf', 'wb') 
        pdf2Output.write(outfile2)
        # Wait for file to finish writing
        outfile2.close()
        
        # Make sure that both output pdf have the correct result
        # using diff_pdf_visually lib
        # The lib take 2 parameters. That is path for both pdf file in local directory
        # The lib will return true if both pdf are the same
        # Test first splited file
        verFile = testDir + 'local_splited_file_1.pdf'
        verFile2 = testDir + 'test_splited_file_1.pdf'
        self.assertTrue(pdfdiff(verFile, verFile2))
        # Test second splited file
        verFile3 = testDir + 'local_splited_file_2.pdf'
        verFile4 = testDir + 'test_splited_file_2.pdf'
        self.assertTrue(pdfdiff(verFile3, verFile4))

        # remove unziped files
        os.remove('splited_file_1.pdf')
        os.remove('splited_file_2.pdf')
        # remove output files after finish testing
        os.remove(verFile2)
        os.remove(verFile4)

    def test_delete_anonymous_valid(self):
        """Check that anonymous can upload pdf file, input multiple page number and get the correct deleted page(s) pdf file"""
         # Path for pdf file from local directory
        testDir = '/Users/palm/Data/University/3_1/CN340/Project/pdf_test/'

        # Open file from local directory 
        # Chosen PDF have 2 pages
        openFile = open(testDir + 'merged_file.pdf', 'rb')
        # Page number is 1
        # Output PDF should have 1 page, that is 2nd page of the original file
        # Note that in PDFDeleteForm, pageNum is CharField
        # Page number has to be String
        inPageNum = '1'

        response = self.client.post('/pdf/delete/', {
            'file1':openFile, 
            'pageNum':inPageNum,
        })

        # Make sure that status code is 200
        self.assertEqual(response.status_code, 200)
        
        # Make sure that response attached the right file
        self.assertEqual(response.get('Content-Disposition'), 'attachment;filename="deleted_file.pdf"')

        # Read output file back from FileResponse
        content = list(response.streaming_content)
        bContent = b''.join(content)
        reader = PdfFileReader(io.BytesIO(bContent))

        # Original pdf have 2 pages
        # Delete 1st page
        # Deleted file should have 1 page
        self.assertEqual(reader.getNumPages(), 1)

        # diff_pdf_visually lib needs the file to exist locally
        # Write the output file to local storage
        output = PdfFileWriter()
        for i in range(reader.getNumPages()):
            output.addPage(reader.getPage(i))
        outfile = open(testDir + 'test_deleted_file.pdf', 'wb') 
        output.write(outfile)
        # Wait for file to finish writing
        outfile.close()
        
        # Make sure that output pdf have the correct result
        # using diff_pdf_visually lib
        # The lib take 2 parameters. That is path for both pdf file in local directory
        verFile = testDir + 'deleted_file.pdf'
        verFile2 = testDir + 'test_deleted_file.pdf'
        # The lib will return true if both pdf are the same 
        self.assertTrue(pdfdiff(verFile, verFile2))

        # remove output file after finish testing
        os.remove(verFile2)

    def test_merge_anonymous_invalid(self):
        """Check that anonymous can not upload non-pdf file into merge page"""
        # Path for image file from local directory
        testDir = '/Users/palm/Data/University/3_1/CN340/Project/pdf_test/'

        # Open image (non-pdf) file from local directory
        openFile = open(testDir + 'background.jpg', 'rb')

        response = self.client.post('/pdf/merge/', {
            'file1':openFile, 
            'file2':openFile,
        })

        # Make sure that status code is 200
        self.assertEqual(response.status_code, 200)

        # Make sure that response not attached any file
        self.assertIsNone(response.get('Content-Disposition'), 'attachment;filename="merged_file.pdf"')

    def test_split_anonymous_invalid_file(self):
        """Check that anonymous can not upload non-pdf file into split page"""
        # Path for image file from local directory
        testDir = '/Users/palm/Data/University/3_1/CN340/Project/pdf_test/'

        # Open image (non-pdf) file from local directory
        openFile = open(testDir + 'background.jpg', 'rb')

        # Does not matter right now, because the file is not pdf anyway
        inPageNum = 1

        response = self.client.post('/pdf/split/', {
            'file1':openFile, 
            'pageNum':inPageNum,
        })

        # Make sure that status code is 200
        self.assertEqual(response.status_code, 200)
        
        # Make sure that response not attached any file
        self.assertIsNone(response.get('Content-Disposition'), 'attachment;filename="splited_files.zip"')
    
    def test_split_anonymous_invalid_page_number(self):
        """Check that anonymous can not enter invalid page number into split page"""
        # Path for pdf file from local directory
        testDir = '/Users/palm/Data/University/3_1/CN340/Project/pdf_test/'

        # Open file from local directory 
        # Chosen PDF have 2 pages
        openFile = open(testDir + 'merged_file.pdf', 'rb')

        # Enter invalid page number
        inPageNum = -1

        response = self.client.post('/pdf/split/', {
            'file1':openFile, 
            'pageNum':inPageNum,
        })

        # Make sure that status code is 200
        self.assertEqual(response.status_code, 200)
        
        # Make sure that the message is Invalid
        self.assertEqual(response.context['message'], 'Invalid')

        # Make sure that response not attached any file
        self.assertIsNone(response.get('Content-Disposition'), 'attachment;filename="splited_files.zip"')

    def test_delete_anonymous_invalid_file(self):
        """Check that anonymous can not upload non-pdf file into delete page"""
        # Path for image file from local directory
        testDir = '/Users/palm/Data/University/3_1/CN340/Project/pdf_test/'

        # Open image (non-pdf) file from local directory
        openFile = open(testDir + 'background.jpg', 'rb')

        # Does not matter now, because the file is not pdf anyway
        inPageNum = '1'

        response = self.client.post('/pdf/delete/', {
            'file1':openFile, 
            'pageNum':inPageNum,
        })

        # Make sure that status code is 200
        self.assertEqual(response.status_code, 200)
        
        # Make sure that response not attached any file
        self.assertIsNone(response.get('Content-Disposition'), 'attachment;filename="deleted_files.pdf"')
    
    def test_delete_anonymous_invalid_page_number(self):
        """Check that anonymous can not enter invalid page number into delete page"""
        # Path for pdf file from local directory
        testDir = '/Users/palm/Data/University/3_1/CN340/Project/pdf_test/'

        # Open file from local directory 
        # Chosen PDF have 2 pages
        openFile = open(testDir + 'merged_file.pdf', 'rb')

        # Enter invalid page number
        # PDF have 2 pages, page 3 does not exist
        inPageNum = '3'

        response = self.client.post('/pdf/delete/', {
            'file1':openFile, 
            'pageNum':inPageNum,
        })

        # Make sure that status code is 200
        self.assertEqual(response.status_code, 200)
        
        # Make sure that the message is Invalid
        self.assertEqual(response.context['message'], 'Invalid')

        # Make sure that response not attached any file
        self.assertIsNone(response.get('Content-Disposition'), 'attachment;filename="deleted_files.pdf"')