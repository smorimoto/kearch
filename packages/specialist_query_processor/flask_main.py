# Example for api is
# $(ip adress of specialist_query_processor/retrieve?queries=google+facebook&max_urls=100

import flask
import specialist_query_processor

app = flask.Flask(__name__)


@app.route('/retrieve', methods=['GET'])
def post():
    queries = flask.request.args.get('queries')
    queries = queries.split(' ')
    max_urls = flask.redirect.args.get('max_urls', int)
    result = specialist_query_processor.retrieve(queries, max_urls)
    return flask.render_template('result.html', result=result)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=10080)  # どこからでもアクセス可能に
