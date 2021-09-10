# Python BzTCP
This package provides a pure-Python implementation of the Benzinga TCP protcol.

**->> Service Deprecated <--**

# Features

  * Compatible with Python 2.6+ and Python 3.
  * No external dependencies.
  * Supports large messages.

# Getting Started
To install the library, invoke setup.py as usual:

    python setup.py install

To test the Python client, you can run the package's built-in demo by running the
module directly. In Python 3 and 2.7+:

    python -m bztcp USERNAME KEY

To test the Python client with configurable retries, delay and backoff you can run
the package's built-in demo by running the module directly. In Python 3 and 2.7+:

    python -m bztcp USERNAME KEY RETRIES DELAY BACKOFF

In Python 2.6 and under, you will need the following:

    python -m bztcp.__main__ USERNAME KEY

Versions 2.5 and under are untested, but should be possible to support without
drastic modifications. Please contact support if you are encountering errors you
believe to be related to Python version.

# Usage
The bulk of the work is done by the `bztcp.client.Client` class. To get an idea
of how to use it, you can check out the demo client at `bztcp/__main__.py`. Here's
a similar example that prints out titles as they come in:

```python
from __future__ import print_function
from bztcp.client import Client

client = Client(username='USERNAME', key='APIKEY')
for content in client.content_items():
    title = content.get('title', None)
    print(title)
```

To get an idea of how to pass configurable retries, delay and backoff in the
`bztcp.client.Client` class, here's a similar example using the above code snippet:  
```python
from __future__ import print_function
from bztcp.client import Client

client = Client(username='USERNAME', key='APIKEY', retries=5, delay=90, backoff=2)
for content in client.content_items():
    title = content.get('title', None)
    print(title)
```

If you want to get a more granular look at the connection status, 
you can handle individual messages instead of just content items,
as well as disconnect the stream on command:

```python
from bztcp.client import Client, STATUS_STREAM
import os

client = Client(username='USERNAME', key='APIKEY')

while True:
    try:
        msg = client.next_msg()
        
        if msg.status == STATUS_STREAM:
            print(f"Content item: {msg.data}")
        else:
            print(f"Status: {msg.status}")
    except KeyboardInterrupt as ke:
        print(f"Cancelled, disconnecting.")
        client.disconnect()
    except BzException as bze:
        print(f"BZ Error: {bze}")
        break
```
