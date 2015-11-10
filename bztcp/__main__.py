from __future__ import print_function, absolute_import

# Python 2.6 and under do not have argparse.
try:
    import argparse
except ImportError:
    from . import argparse

from .client import Client


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Connects to Benzinga TCP.', prog='bztcp')
    parser.add_argument('username', help='Username to authenticate with.')
    parser.add_argument('key', help='Key to authenticate with.')
    args = parser.parse_args()
    
    print('Starting benzinga TCP test client.')
    client = Client(username=args.username, key=args.key)
    for content in client.content_items():
        print(
            'Title:', content.get('title', 'No title.'),
            '; Tickers:', content.get('tickers', []),
            '; Channels:', content.get('channels', [])
        )
        # Other fields include 'content', 'updated'...
