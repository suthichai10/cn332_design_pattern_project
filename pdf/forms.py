from django import forms

class PDFMergeForm(forms.Form):
    file1 = forms.FileField(label="PDF file 1")
    file2 = forms.FileField(label="PDF file 2")

    def __init__(self, *args, **kwargs):
        super(PDFMergeForm, self).__init__(*args, **kwargs)
        self.fields['file1'].widget.attrs.update({'accept': '.pdf'})
        self.fields['file2'].widget.attrs.update({'accept': '.pdf'})

class PDFSplitForm(forms.Form):
    file1 = forms.FileField(label="PDF file")
    pageNum = forms.IntegerField(label="Page number")

    def __init__(self, *args, **kwargs):
        super(PDFSplitForm, self).__init__(*args, **kwargs)
        self.fields['file1'].widget.attrs.update({'accept': '.pdf'})
        self.fields['pageNum'].widget.attrs.update(min='1')
        self.fields['pageNum'].widget.attrs.update({'autocomplete': 'off'})
        self.fields['pageNum'].widget.attrs.update({'placeholder': 'Page Number'})

class PDFDeleteForm(forms.Form):
    file1 = forms.FileField(label="PDF file")
    pageNum = forms.CharField(label="Page number")

    def __init__(self, *args, **kwargs):
        super(PDFDeleteForm, self).__init__(*args, **kwargs)
        self.fields['file1'].widget.attrs.update({'accept': '.pdf'})
        self.fields['pageNum'].widget.attrs.update({'autocomplete': 'off'})
        self.fields['pageNum'].widget.attrs.update({'placeholder': 'Page Number (e.g. 1, 3-5)'})