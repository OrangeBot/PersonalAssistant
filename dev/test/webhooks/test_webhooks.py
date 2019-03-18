ip = "91.79.216.203"
port = 80

import http.server


# json {"event_name": "...", "user_id"=..., "event_data": {...}}
def method_to_call(data):
    print("-" * 80)
    print("Todoist webhook received message and outputs the following:")
    print(data)
    print("-" * 80)


# Handler = http.server.BaseHTTPRequestHandler
x = http.server.SimpleHTTPRequestHandler


class TodoistWebhookHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        message = "<html><body><h1>hi!</h1></body></html>"
        self.wfile.write(message.encode('utf-8'))

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        self._set_headers()
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        print("Todoist webhook handler received POST request and it looks like this:")
        print(post_data)
        # self.wfile.write("<html><body><h1>POST!</h1><pre>" + post_data + "</pre></body></html>")
