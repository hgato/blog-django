from elasticsearch import Elasticsearch


class ElasticSearch:
    index_pattern = '*'
    from_ = 0
    size = 10
    fields = []

    def __init__(self):
        self.connection = Elasticsearch('elasticsearch', port=9200)

    def get_index(self):
        # get indexes by alias
        list_of_indices = list(self.connection.indices.get_alias(self.index_pattern))
        # get second newest index - first may be incomplete
        list_of_indices.sort(reverse=True)
        return list_of_indices[1]

    def run(self, query):
        index = self.get_index()
        query = self.form_query(query)
        results = self.connection.search(index=index, body=query,
                                         size=self.size, from_=self.from_)
        return self.clean_results(results)

    def clean_results(self, results):
        raise NotImplementedError('Method "clean_results" must be implemented')

    def form_query(self, query):
        raise NotImplementedError('Method "form_query" must be implemented')


class PostSearch(ElasticSearch):
    index_pattern = 'post_post*'
    fields = ['text', 'name', 'author_name']

    def count_total(self, results):
        return results['hits']['total']

    def clean_results(self, results):
        total = self.count_total(results)
        clean_results = [hit['_source']['id'] for hit in results['hits']['hits']]
        return clean_results, total

    def form_query(self, query):
        # search all on empty query
        if not query:
            return {
                'query': {
                    'match_all': {}
                }
            }
        # user english analyzer by default and standard one for names
        return {
            'query': {
                'bool': {
                    'should': [
                        {
                            'query_string': {
                                'fields': self.fields,
                                'query': query,
                                'analyzer': 'english',
                                'default_operator': 'AND',
                            }
                        },
                        {
                            'query_string': {
                                'fields': self.fields,
                                'query': query,
                                'analyzer': 'standard',
                                'default_operator': 'AND',
                            }
                        }
                    ]
                }
            }
        }
