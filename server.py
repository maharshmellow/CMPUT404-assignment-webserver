#  coding: utf-8 
import socketserver
import os
# Copyright 2013 Maharsh Patel, Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip().decode()

        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages
        http_method, request_target = self.data.split()[0:2]

        if http_method == "GET":
            print("\n\nGot a request of: %s" % self.data)
            print(http_method, request_target)

            self.processRequest(request_target)
        else: 
            # invalid method
            self.sendResponse(405)

    def processRequest(self, request_target):
        path = "www" + request_target
        
        if os.path.isdir(path):
            if (path.endswith("/")):
                path = path + "index.html"
                self.sendFile(path)
            else:
                correct_location = request_target + "/"
                self.sendResponse(301, redirect_location=correct_location)
        elif os.path.isfile(path):
            self.sendFile(path)
        else:
            print("Doesn't Exist")
            self.sendResponse(404)

    def sendFile(self, path):
        if os.path.isfile(path):
            data = ""
            with open(path, "r") as f:
                data = f.read()

            # By nosklo, https://stackoverflow.com/questions/541390/extracting-extension-from-filename-in-python
            file_extension = os.path.splitext(path)[1]
            if not file_extension:
                file_extension = "html"
            else:
                file_extension = file_extension.replace(".", "")
                
            self.sendResponse(200, file_contents=data, file_type=file_extension)
        else:
            self.sendResponse(404)


    def sendResponse(self, status_code, file_contents=None, file_type=None, redirect_location=None):
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
        status_text = {200: "OK", 301: "Moved Permanently", 404: "Not Found", 405: "Method Not Allowed"}

        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages
        response = "HTTP/1.1 {} {}\r\n".format(status_code, status_text[status_code])
        response += "Connection: Closed\r\n"

        if redirect_location:
            response += "Location: {}\r\n".format(redirect_location)
        elif file_contents:
            response += "Content-Type: text/{}\r\n".format(file_type)
            response += "Content-Length: " + str(len(file_contents.encode("utf-8"))) + "\r\n\n"
            response += file_contents

        self.request.sendall(bytearray(response, 'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
