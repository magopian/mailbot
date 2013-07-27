# -*- coding: utf-8 -*-

import sys

# encoded padding is to cope with this ugly bug:
# http://bugs.python.org/issue1467619
# For some reason, in py27, the whitespace separating encoded pieces is eaten
# up
encoded_padding = ''
text_type = str
if sys.version < '3':
    encoded_padding = ' '
    text_type = unicode  # noqa
