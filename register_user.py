#!/usr/bin/env python

import sys

from mow.models import User

def _main():
    if len(sys.argv) == 3:
        user = User(sys.argv[1], sys.argv[2]).save()
        sys.exit('User "%s" is registered.' % user.name)
    else:
        sys.exit('Usage: %s user_name password' % sys.argv[0])

if __name__ == '__main__':
    _main()
