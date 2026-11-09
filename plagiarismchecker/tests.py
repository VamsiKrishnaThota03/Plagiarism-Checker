import io
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from plagiarismchecker.algorithm import fileSimilarity, main
from plagiarismchecker.algorithm.ConsineSim import cosineSim

SOURCE = ('Machine learning is a field of study in artificial intelligence concerned with the '
          'development of statistical algorithms that can learn from data and generalize to unseen data.')


def docx_bytes(text):
    from docx import Document
    buffer = io.BytesIO()
    document = Document()
    document.add_paragraph(text)
    document.save(buffer)
    return buffer.getvalue()


class AlgorithmTests(TestCase):
    def test_identical_texts_are_100_percent(self):
        self.assertAlmostEqual(fileSimilarity.findFileSimilarity(SOURCE, SOURCE), 100.0)

    def test_unrelated_and_empty_texts(self):
        self.assertEqual(fileSimilarity.findFileSimilarity('apples oranges', 'quantum physics'), 0.0)
        self.assertEqual(fileSimilarity.findFileSimilarity('', SOURCE), 0.0)
        self.assertEqual(fileSimilarity.findFileSimilarity('the and of', 'is a the'), 0.0)

    def test_cosine_sim(self):
        self.assertAlmostEqual(cosineSim('a b c', 'a b c'), 1.0)
        self.assertEqual(cosineSim('a b', 'x y'), 0.0)

    def test_get_queries_chunks_long_sentences(self):
        queries = main.getQueries(SOURCE, 9)
        self.assertTrue(queries)
        self.assertTrue(all(5 <= len(q) <= 9 for q in queries))
        self.assertEqual(main.getQueries('Too short.', 9), [])

    @override_settings(GOOGLE_API_KEY='k', GOOGLE_CSE_ID='cx')
    def test_find_similarity_with_mocked_search(self):
        items = [{'link': 'https://example.org/ml', 'snippet': SOURCE}]
        with mock.patch('plagiarismchecker.algorithm.webSearch.search', return_value=items) as search:
            percent, links = main.findSimilarity(SOURCE)
        self.assertGreater(search.call_count, 0)
        self.assertGreater(percent, 50)
        self.assertLessEqual(percent, 100)
        self.assertIn('https://example.org/ml', links)

    @override_settings(GOOGLE_API_KEY='k', GOOGLE_CSE_ID='cx')
    def test_all_searches_failing_does_not_divide_by_zero(self):
        with mock.patch('plagiarismchecker.algorithm.webSearch.search', side_effect=OSError):
            self.assertEqual(main.findSimilarity(SOURCE), (0.0, {}))

    @override_settings(GOOGLE_API_KEY='k', GOOGLE_CSE_ID='cx', MAX_SEARCH_QUERIES=2)
    def test_query_cap(self):
        with mock.patch('plagiarismchecker.algorithm.webSearch.search', return_value=[]) as search:
            main.findSimilarity(SOURCE * 5)
        self.assertEqual(search.call_count, 2)


class ViewTests(TestCase):
    def test_pages_render(self):
        self.assertContains(self.client.get(reverse('plagiarism-check-mainpage')), 'Check text against the web')
        self.assertContains(self.client.get(reverse('compare')), 'Compare two documents')

    def test_form_endpoints_redirect_on_get(self):
        for name in ('Test', 'filetest', 'twofiletest1', 'twofilecompare1'):
            self.assertEqual(self.client.get(reverse(name)).status_code, 302, name)

    @override_settings(GOOGLE_API_KEY='', GOOGLE_CSE_ID='')
    def test_web_check_without_credentials_shows_message(self):
        response = self.client.post(reverse('Test'), {'q': SOURCE})
        self.assertContains(response, 'not configured')

    @override_settings(GOOGLE_API_KEY='k', GOOGLE_CSE_ID='cx')
    def test_web_check_text_and_file(self):
        with mock.patch('plagiarismchecker.algorithm.main.findSimilarity',
                        return_value=(42.123, {'https://example.org': 42.123})) as find:
            response = self.client.post(reverse('Test'), {'q': SOURCE})
            self.assertContains(response, '42.1%')
            self.assertContains(response, 'https://example.org')
            upload = SimpleUploadedFile('essay.txt', SOURCE.encode())
            response = self.client.post(reverse('filetest'), {'docfile': upload})
            self.assertContains(response, 'essay.txt')
            # .txt content is decoded, not passed as "b'...'"
            self.assertEqual(find.call_args[0][0], SOURCE)

    def test_empty_text_is_rejected(self):
        response = self.client.post(reverse('twofiletest1'), {'q1': '', 'q2': 'x'})
        self.assertContains(response, 'This field is required')

    def test_compare_texts(self):
        response = self.client.post(reverse('twofiletest1'), {'q1': SOURCE, 'q2': SOURCE})
        self.assertContains(response, 'Very similar')

    def test_compare_mixed_file_types(self):
        response = self.client.post(reverse('twofilecompare1'), {
            'docfile1': SimpleUploadedFile('a.txt', SOURCE.encode()),
            'docfile2': SimpleUploadedFile('b.docx', docx_bytes(SOURCE)),
        })
        self.assertContains(response, 'Very similar')

    def test_bad_upload_type(self):
        response = self.client.post(reverse('twofilecompare1'), {
            'docfile1': SimpleUploadedFile('a.exe', b'MZ'),
            'docfile2': SimpleUploadedFile('b.txt', b'hello world'),
        })
        self.assertContains(response, 'is not a .txt, .docx or .pdf file')

    def test_corrupt_docx(self):
        response = self.client.post(reverse('twofilecompare1'), {
            'docfile1': SimpleUploadedFile('a.docx', b'not a zip'),
            'docfile2': SimpleUploadedFile('b.txt', b'hello world'),
        })
        self.assertContains(response, 'Could not read')
