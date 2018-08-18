import json
import urllib

import mysql.connector
import requests

from kearch_common.data_format import wrap_json


class KearchRequester(object):
    """Interface for communicating between containers or servers."""

    def __init__(self,
                 host='localhost', port=None,
                 requester_name='', conn_type='json'):
        super(KearchRequester, self).__init__()
        self.host = host
        self.port = port
        self.conn_type = conn_type
        self.requester_name = requester_name

    def __repr__(self):
        return '<KearchRequester host: %r, port: %r, conn_type: %r>'.\
            format(self.host, self.port, self.conn_type)

    def request(self, path='', method='GET',
                params=None, payload=None,
                headers=None, timeout=None):
        if self.conn_type == 'json':
            return self.request_json(path, method, params, payload,
                                     headers, timeout)
        elif self.conn_type == 'sql':
            return self.request_sql(path, method, params, payload,
                                    headers, timeout)
        else:
            raise ValueError('conn_type should be "json" or "sql".')

    def request_json(self, path='', method='GET',
                     params=None, payload=None,
                     headers=None, timeout=None):
        if self.port is None:
            url = urllib.parse.urljoin(self.host, path)
        else:
            url = urllib.parse.urljoin(
                'http://{}:{}'.format(self.host, self.port), path)

        if method == 'GET':
            # GET の場合は payload を url param にする
            resp = requests.get(url, params=params, timeout=timeout)
        else:
            # GET 以外は json に payload を含めて送る
            meta = {
                'requester': self.requester_name,
            }
            data = wrap_json(payload, meta)
            resp = requests.request(
                method, url, params=params, json=data, timeout=timeout)

        return resp.json()

    def request_sql(self, path='', method='GET',
                    params=None, payload=None,
                    headers=None, timeout=None):

        parsed = urllib.parse.urlparse(path)
        parsed_path = parsed.path
        config = {
            'host': self.host,
            'database': 'kearch_sp_dev',
            'user': 'root',
            'password': 'password',
            'charset': 'utf8',
            'use_unicode': True,
            'get_warnings': True,
        }

        db = mysql.connector.Connect(**config)
        cur = db.cursor()
        ret = None

        try:
            if parsed_path == '/push_webpage_to_database':
                # get webpage records from payload
                webpage_records = [(w['url'],
                                    json.dumps(w['title_words']),
                                    w['summary'],
                                    json.dumps(w['tfidf']))
                                   for w in payload['data']]
                statement = """
                REPLACE INTO `webpages`
                (`url`, `title_words`, `summary`, `tfidf`)
                VALUES (%s)
                """

                cur.executemany(statement, webpage_records)
                db.commit()
                ret = cur.rowcount
            elif parsed_path == '/get_next_urls':
                max_urls = int(params['max_urls'])
                select_statement = """
                SELECT `url` FROM `url_queue` ORDER BY `updated_at` LIMIT %s
                """
                delete_statement = """
                DELETE FROM `url_queue` ORDER BY `updated_at` LIMIT %s
                """

                cur.execute(select_statement, (max_urls,))
                result_urls = [row[0] for row in cur.fetchall()]
                ret = {
                    'urls': result_urls
                }
                cur.execute(delete_statement, (max_urls,))
                db.commit()
            elif parsed_path == '/push_urls_to_queue':
                url_queue_records = [(url,) for url in payload['urls']]
                statement = """
                REPLACE INTO `url_queue` (`url`) VALUES (%s)
                """

                cur.executemany(statement, url_queue_records)
                db.commit()
                ret = cur.rowcount
            else:
                raise ValueError('Invalid path: {}'.format(path))
        except Exception as e:
            raise
        finally:
            cur.close()
            db.close()

        return ret
