#######
MailBot
#######

.. image:: https://secure.travis-ci.org/magopian/mailbot.png?branch=master
   :alt: Build Status
   :target: https://travis-ci.org/magopian/mailbot

MailBot: register callbacks to be executed on mail reception.

* Authors: Mathieu Agopian and `contributors
  <https://github.com/magopian/mailbot/contributors>`_
* Licence: BSD
* Compatibility: Python 2.7 and Python 3.3
* Project URL: https://github.com/magopian/mailbot
* Documentation: http://mailbot.rtfd.org/


Hacking
=======

Setup your environment:

::

    git clone https://github.com/magopian/mailbot.git
    cd mailbot

Hack and run the tests using `Tox <https://pypi.python.org/pypi/tox>`_ to test
on all the supported python versions:

::

    make test

There's also a live test suite, that you may run using the following command:

::

    make livetest

Please note that to run live tests, you need to create a
``livetest_settings.py`` file with the following content:

::

    # mandatory
    HOST = 'your host here'
    USERNAME = 'your username here'
    PASSWORD = 'your password here'

    # optional
    # check http://imapclient.readthedocs.org/en/latest/#imapclient.IMAPClient)
    PORT = 143  # port number, usually 143 or 993 if ssl is enabled
    USE_UID = True
    SSL = False
    STREAM = False

For convenience, you can copy the provided sample, and modify it:

::

    $ cp livetest_settings.py.sample livetest_settings.py
