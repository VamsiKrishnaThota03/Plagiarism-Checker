from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from plagiarismchecker.algorithm import fileSimilarity, main, webSearch

from .forms import CompareFileForm, CompareTextForm, WebFileForm, WebTextForm


def _web_page(request, text_form=None, file_form=None, active='text', **extra):
    context = {
        'text_form': text_form or WebTextForm(),
        'file_form': file_form or WebFileForm(),
        'active_tab': active,
        'search_configured': webSearch.is_configured(),
        **extra,
    }
    return render(request, 'pc/index.html', context)


def _compare_page(request, text_form=None, file_form=None, active='text', **extra):
    context = {
        'text_form': text_form or CompareTextForm(),
        'file_form': file_form or CompareFileForm(),
        'active_tab': active,
        **extra,
    }
    return render(request, 'pc/doc_compare.html', context)


def _web_check(text):
    """Run the web check and return template context with results or an error."""
    try:
        percent, links = main.findSimilarity(text)
    except webSearch.SearchNotConfigured:
        return {'error': 'Web search is not configured on this server '
                         '(GOOGLE_API_KEY and GOOGLE_CSE_ID are missing).'}
    sources = sorted(((link, round(p, 1)) for link, p in links.items()),
                     key=lambda item: item[1], reverse=True)
    return {'percent': round(percent, 2), 'sources': sources, 'checked': True}


def home(request):
    return _web_page(request)


@require_http_methods(['GET', 'POST'])
def test(request):
    """Web check for pasted text (form field ``q``)."""
    if request.method == 'GET':
        return redirect('plagiarism-check-mainpage')
    form = WebTextForm(request.POST)
    if not form.is_valid():
        return _web_page(request, text_form=form)
    return _web_page(request, text_form=form, **_web_check(form.cleaned_data['q']))


@require_http_methods(['GET', 'POST'])
def filetest(request):
    """Web check for an uploaded .txt/.docx/.pdf (form field ``docfile``)."""
    if request.method == 'GET':
        return redirect('plagiarism-check-mainpage')
    form = WebFileForm(request.POST, request.FILES)
    if not form.is_valid():
        return _web_page(request, file_form=form, active='file')
    return _web_page(request, file_form=WebFileForm(), active='file',
                     filename=request.FILES['docfile'].name,
                     **_web_check(form.cleaned_data['docfile_text']))


def fileCompare(request):
    return _compare_page(request)


@require_http_methods(['GET', 'POST'])
def twofiletest1(request):
    """Compare two pasted texts (``q1``, ``q2``)."""
    if request.method == 'GET':
        return redirect('compare')
    form = CompareTextForm(request.POST)
    if not form.is_valid():
        return _compare_page(request, text_form=form)
    result = fileSimilarity.findFileSimilarity(form.cleaned_data['q1'], form.cleaned_data['q2'])
    return _compare_page(request, text_form=form, result=round(result, 2))


@require_http_methods(['GET', 'POST'])
def twofilecompare1(request):
    """Compare two uploaded documents (``docfile1``, ``docfile2``); types may differ."""
    if request.method == 'GET':
        return redirect('compare')
    form = CompareFileForm(request.POST, request.FILES)
    if not form.is_valid():
        return _compare_page(request, file_form=form, active='file')
    result = fileSimilarity.findFileSimilarity(form.cleaned_data['docfile1_text'],
                                               form.cleaned_data['docfile2_text'])
    return _compare_page(request, active='file', result=round(result, 2),
                         filenames=(request.FILES['docfile1'].name, request.FILES['docfile2'].name))
