import time
from elasticsearch import Elasticsearch


def create_instance():
    return Elasticsearch('elasticsearch', port=9200)


def get_indices(es):
    list_of_indices = list(es.indices.get_alias("*"))
    list_of_indices.sort(reverse=True)
    base_indices = set(i.split('-')[0] for i in list_of_indices if len(i.split('-')) > 1)
    return list_of_indices, base_indices


def get_to_delete(list_of_indices, base_indices):
    to_delete = []
    for i in base_indices:
        indices = []
        for al in list_of_indices:
            if al.startswith(i):
                indices.append(al)
        indices = indices[3:]
        to_delete += indices
    return to_delete


def delete_indices(es, to_delete):
    for i in to_delete:
        es.indices.delete(index=i, ignore=[400, 404])
    return to_delete


def run_delete_workflow():
    try:
        es = create_instance()
        to_delete = get_to_delete(*get_indices(es))
        return delete_indices(es, to_delete)
    except Exception as e:
        return e


if __name__ == '__main__':
    while True:
        result = run_delete_workflow()
        print('Deleted following indices:', result)
        time.sleep(60)
