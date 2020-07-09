from __future__ import (
    print_function, unicode_literals, absolute_import, division
)

import socket
import datetime
import json


# Python 2.6 and below do not have timedelta.total_seconds.
def timedelta_total_seconds(timedelta):
    return (
        timedelta.microseconds + 0.0 +
        (timedelta.seconds + timedelta.days * 24 * 3600) * 10 ** 6
    ) / 10 ** 6

# Default connection parameters
BZ_HOST='tcp-v1.benzinga.io'
BZ_PORT=11337
BZ_PING_INTERVAL=5.0


# Protocol end-of-transmission signal.
BZ_EOT = b'=BZEOT\r\n'

# Protocol status values
STATUS_INVALID_KEY = b'INVALID KEY'
STATUS_BAD_KEY_FORMAT = b'INVALID KEY FORMAT'
STATUS_DUPLICATE_CONN = b'DUPLICATE CONNECTION'
STATUS_READY = b'READY'
STATUS_CONNECTED = b'CONNECTED'
STATUS_AUTH = b'AUTH'
STATUS_STREAM = b'STREAM'
STATUS_PING = b'PING'

# Exception messages.
ERR_NOT_CONNECTED = ('Not connected', -1)
ERR_INVALID_KEY = ('Bad credentials provided', -2)
ERR_BAD_PACKET = ('Malformed packet', -3)
ERR_TOO_MANY_CONNS = ('Too many connections for key', -4)
ERR_UNKNOWN_ERROR = ('An unknown error occurred', -5)
ERR_SERVER_ERROR = ('The Benzinga TCP service is unavailable', -6)


# Exception class for our errors.
class BzException(Exception):
    def __init__(self, message, code):
        super(BzException, self).__init__(message)
        self.code = code


# Message class for protocol messages.
# The Benzinga TCP protocol is a stream of these messages.
class Message(object):
    def __init__(self, status, data = None):
        self.status = status
        self.data = data

    def to_bytes(self):
        m = b''
        m += self.status
        if self.data != None:
            m += b': '
            m += json.dumps(self.data).encode('utf-8')
        m += BZ_EOT
        return m

    @staticmethod
    def from_bytes(m):
        # Check for EOT signal.
        if not m.endswith(BZ_EOT):
            raise BzException(*ERR_BAD_PACKET)
        
        # Remove EOT signal.
        m = m[:-len(BZ_EOT)]

        # Check for data separator.
        if b':' in m:
            s, d = m.split(b':', 1)

            # Parse the data.
            data = json.loads(d.decode('utf-8').strip())

            return Message(s.strip(), data)
        else:
            return Message(m.strip())


# Client object for connecting to TCP services.
class Client(object):
    def __init__(self, username, key, host=None, port=None):
        # Default if unspecified.
        if host == None:
            host = BZ_HOST
        if port == None:
            port = BZ_PORT

        self._host = host
        self._port = port

        self._username = username
        self._key = key

        ping_delta = datetime.timedelta(seconds=BZ_PING_INTERVAL)
        self._nextping = datetime.datetime.now() + ping_delta

        # Connect and authenticate.
        self.connect()
        self.authenticate()

    # Receives a single message from the stream.
    def recv(self):
        while True:
            # Do we have a full message in our buffer already?
            if BZ_EOT in self._buf:
                # Return the first full message buffered.
                line, self._buf = self._buf.split(BZ_EOT, 1)
                return Message.from_bytes(line + BZ_EOT)

            # Buffer more data if not.
            buf = self._sock.recv(4096)

            if not buf:
                return None

            self._buf += buf

    # Sends a single message to the stream.
    def send(self, msg):
        if not getattr(self, '_sock', None):
            raise BzException(*ERR_NOT_CONNECTED)

        self._sock.sendall(msg.to_bytes())

    # Connects to the server (possibly again.)
    def connect(self):
        self._buf = b''
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self._host, self._port))

    # Authenticates with the upstream server using credentials passed in.
    def authenticate(self):
        msg = self.recv()
        if msg.status != STATUS_READY:
            raise BzException(*ERR_SERVER_ERROR)
       
        creds = {
            'username': self._username,
            'key': self._key
        }

        self.send(Message(STATUS_AUTH, creds))

        msg = self.recv()
        if msg.status == STATUS_INVALID_KEY:
            raise BzException(*ERR_INVALID_KEY)
        elif msg.status == STATUS_BAD_KEY_FORMAT:
            raise BzException(*ERR_INVALID_KEY)
        elif msg.status == STATUS_DUPLICATE_CONN:
            raise BzException(*ERR_TOO_MANY_CONNS)
        elif msg.status == STATUS_CONNECTED:
            return
        else:
            raise BzException(*ERR_UNKNOWN_ERROR)

    # Send a ping.
    def ping(self):
        data = {
            'pingTime': datetime.datetime.now().isoformat()
        }
        self.send(Message(STATUS_PING, data))

    # Returns the next message, sending pings at the ping interval.
    def next_msg(self):
        while True:
            ping_delta = datetime.timedelta(seconds=BZ_PING_INTERVAL)
            now = datetime.datetime.now()

            # Need to ping.
            if now > self._nextping:
                self._nextping = now + ping_delta
                self.ping()

            # Calculate time to next ping.
            secs_till_ping = timedelta_total_seconds(self._nextping - now)

            # Set timeout for next ping.
            self._sock.settimeout(secs_till_ping + 0.5)

            # Try to receive a message.
            try:
                result = self.recv()
                if result is not None and getattr(result, "data", "") != "":
                    #result2 = self.recv()
                    return result
                else:
                    raise BzException(*ERR_NOT_CONNECTED)
            except socket.timeout:
                continue
                

    # Gets the next content item in the message stream.
    def next_content(self):
        while True:
            msg = self.next_msg()
            if msg.status == STATUS_STREAM:
                return msg

    def content_items(self):
        while True:
            yield self.next_content().data

