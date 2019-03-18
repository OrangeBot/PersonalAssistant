import json
import logging

import http.server


def get_todoist_webhook_handler(callback):
    class TodoistWebhookHandler(http.server.BaseHTTPRequestHandler):
        def _set_headers(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        def do_GET(self):
            self._set_headers()
            message = "<html><body><h1>Todoist webhook server is aliiiiiive!</h1></body></html>"
            self.wfile.write(message.encode('utf-8'))

        def do_HEAD(self):
            self._set_headers()

        def do_POST(self):
            self._set_headers()
            content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
            post_data = self.rfile.read(content_length)  # <--- Gets the data itself
            data = json.loads(post_data)
            logging.debug("Todoist webhook handler received POST request with event {}".format(data['event_name']))
            callback(data)

    return TodoistWebhookHandler
