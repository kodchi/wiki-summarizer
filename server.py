import http.server
import json
import socketserver
from urllib.parse import urlparse, parse_qs

import wikiarticle

# TODO: make configurable
PORT = 8002


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        query_components = parse_qs(urlparse(self.path).query)

        # we're looking for 'pageName' query parameter
        summaries = []
        if 'pageName' not in query_components:
            response_code = 400
        else:
            response_code = 200
            page_name = query_components['pageName'][0]
            print('page name: %s' % page_name)
            summaries = wikiarticle.get_summaries(page_name)

        self.send_response(response_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        self.wfile.write(bytes(json.dumps(summaries), "utf8"))

        return


if __name__ == '__main__':
    print('Server listening on port %s ...' % PORT)
    httpd = socketserver.TCPServer(('', PORT), Handler)
    httpd.serve_forever()
