# Python BzTCP
This package provides a pure-Python implementation of the Benzinga TCP protcol.

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
