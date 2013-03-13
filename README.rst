#######
MailBot
#######

.. image:: https://secure.travis-ci.org/novagile/mailbot.png?branch=master
   :alt: Build Status
   :target: https://travis-ci.org/novagile/mailbot

MailBot: register callbacks to be executed on mail reception.

* Authors: Mathieu Agopian and `contributors
  <https://github.com/novagile/mailbot/contributors>`_
* Licence: BSD
* Compatibility: Django 1.4+, python2.6 up to python3.3
* Project URL: https://github.com/novagile/mailbot
* Documentation: http://mailbot.rtfd.org/


Hacking
=======

Setup your environment:

::

    git clone https://github.com/novagile/mailbot.git
    cd mailbot

Hack and run the tests using `Tox <https://pypi.python.org/pypi/tox>`_ to test
on all the supported python and Django versions:

::

    make test
