from django import forms
from django.conf import settings

from .extract import ExtractionError, extract_text

FILE_ACCEPT = '.txt,.docx,.pdf'


def _text_field(label, name):
    return forms.CharField(
        label=label, max_length=settings.MAX_TEXT_CHARS, strip=True,
        widget=forms.Textarea(attrs={'rows': 10, 'class': 'form-control', 'id': f'id_{name}',
                                     'placeholder': 'Paste or type text here…'}),
    )


class FileTextMixin:
    """Turns a FileField into extracted text in cleaned_data['<field>_text']."""

    def _clean_upload(self, field):
        upload = self.cleaned_data.get(field)
        if upload is None:
            return upload
        try:
            self.cleaned_data[f'{field}_text'] = extract_text(upload)[:settings.MAX_TEXT_CHARS]
        except ExtractionError as exc:
            raise forms.ValidationError(str(exc))
        return upload


class WebTextForm(forms.Form):
    q = _text_field('Text to check', 'q')


class WebFileForm(FileTextMixin, forms.Form):
    docfile = forms.FileField(label='Document',
                              widget=forms.ClearableFileInput(attrs={'accept': FILE_ACCEPT,
                                                                     'class': 'form-control'}))

    def clean_docfile(self):
        return self._clean_upload('docfile')


class CompareTextForm(forms.Form):
    q1 = _text_field('First text', 'q1')
    q2 = _text_field('Second text', 'q2')


class CompareFileForm(FileTextMixin, forms.Form):
    docfile1 = forms.FileField(label='First document',
                               widget=forms.ClearableFileInput(attrs={'accept': FILE_ACCEPT,
                                                                      'class': 'form-control'}))
    docfile2 = forms.FileField(label='Second document',
                               widget=forms.ClearableFileInput(attrs={'accept': FILE_ACCEPT,
                                                                      'class': 'form-control'}))

    def clean_docfile1(self):
        return self._clean_upload('docfile1')

    def clean_docfile2(self):
        return self._clean_upload('docfile2')
