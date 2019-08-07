from django.test import TestCase
from search.src.search import PostSearch

mock_results = {
    'hits': {
        'total': 2,
        'hits': [
            {
                '_source': {
                    'id': 1
                }
            },
            {
                '_source': {
                    'id': 7
                }
            }
        ]
    }
}


class ElasticsearchIndicesMock:
    def get_alias(self, index_pattern):
        return ['post_post-0000.00.00',
                'post_post-1111.11.11',
                'post_post-2222.22.22', ]


class ElasticsearchMock:
    indices = ElasticsearchIndicesMock()

    def search(self, index, body, size, from_):
        return mock_results


class PostSearchTest(TestCase):
    def test_count_total(self):
        """
        count_result must return total hits count
        """
        search_object = PostSearch()
        self.assertEqual(2, search_object.count_total(mock_results), 'Wrong count')

    def test_clear_results(self):
        search_object = PostSearch()
        self.assertEqual(([1, 7, ], 2,), search_object._clean_results(mock_results), 'Wrong result')

    def test_form_query(self):
        search_object = PostSearch()
        query = 'query'
        expected_query = {
            'query': {
                'bool': {
                    'should': [
                        {
                            'query_string': {
                                'fields': search_object.fields,
                                'query': query,
                                'analyzer': 'english',
                                'default_operator': 'AND',
                            }
                        },
                        {
                            'query_string': {
                                'fields': search_object.fields,
                                'query': query,
                                'analyzer': 'standard',
                                'default_operator': 'AND',
                            }
                        }
                    ]
                }
            }
        }
        self.assertEqual(expected_query, search_object._form_query(query), 'Wrong query dictionary returned')

    def test_form_query_empty(self):
        search_object = PostSearch()
        query = ''
        expected_query = {
            'query': {
                'match_all': {}
            }
        }
        self.assertEqual(expected_query, search_object._form_query(query), 'Wrong query dictionary returned')

    def test_get_index(self):
        search_object = PostSearch()
        search_object.connection = ElasticsearchMock()
        self.assertEqual('post_post-1111.11.11', search_object._get_index())

    def test_run(self):
        search_object = PostSearch()
        search_object.connection = ElasticsearchMock()
        self.assertEqual(([1, 7, ], 2,), search_object.run(''), 'Wrong result')
