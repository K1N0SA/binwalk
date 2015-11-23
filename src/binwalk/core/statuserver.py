# Provides scan status information via a TCP socket service.

import time
import threading
import SocketServer

class StatusRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        message_format = 'Binwalk scan progress: %3d%%   Currently at byte %d of %d total bytes in file %s'
        last_status_message_len = 0
        status_message = ''

        while True:
            time.sleep(0.1)

            try:
                self.request.send('\b' * last_status_message_len)
                self.request.send(' ' * last_status_message_len)
                self.request.send('\b' * last_status_message_len)

                percentage = ((float(self.server.binwalk.status.completed) / float(self.server.binwalk.status.total)) * 100)
                status_message = message_format % (percentage,
                                                   self.server.binwalk.status.completed,
                                                   self.server.binwalk.status.total,
                                                   self.server.binwalk.status.fp.path)
                last_status_message_len = len(status_message)

                self.request.send(status_message)
            except KeyboardInterrupt as e:
                raise e
            except Exception as e:
                pass

        return

class ThreadedStatusServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

class StatusServer(object):

    def __init__(self, port, binwalk):
        self.server = ThreadedStatusServer(('127.0.0.1', port), StatusRequestHandler)
        self.server.binwalk = binwalk

        t = threading.Thread(target=self.server.serve_forever)
        t.setDaemon(True)
        t.start()