Welcome to MailBot's documentation!
=======================================

MailBot is a little python library that let's you execute previously registered
callbacks on reception of emails.

This allows you to do fancy things like doing API calls, running scripts,
sending notifications, ...


Features
--------

MailBot does its best to:

* be fully tested
* apply the pep8 recommendations
* be lightweight, concise and readable

MailBot connects to a SMTP server using the IMAP protocol, thanks to the
excellent `IMAPClient from Menno Smits
<http://imapclient.readthedocs.org/en/latest/>`_.


Other resources
---------------

Fork it on: http://github.com/novagile/mailbot/

Documentation: http://mailbot.rtfd.org/


Installing
----------

From PyPI::

    pip install mailbot

From github::

    pip install -e http://github.com/novagile/mailbot/


Registering callbacks
---------------------

:file:`callbacks.py`:

.. code-block:: python

    from mailbot import register, Callback


    class MyCallback(Callback):

        def callback(self):
            print("Mail received: {O}".format(self.subject))

    register(MyCallback)

By default, callbacks will be executed on each and every mail received, unless
you specify it differently, either using the 'rules' parameter on the callback
class, or by registering with those rules:


Providing the rules as a parameter
----------------------------------

Here's a callback that will only be triggered if the subject matches the
pattern 'Hello ' followed by a word:

.. code-block:: python

    from mailbot import register, Callback


    class MyCallback(Callback):
        rules = {'subject_patterns': [r'Hello (\w)']}

        def callback(self):
            print("Mail received for {0}".format(self.subject_matches[0]))

    register(MyCallback)

This callback will be triggered on a mail received with the subject "Hello
Bryan", but won't if the subject is "Bye Bryan".


Providing the rules when registering
------------------------------------

The similar functionality can be achieved using a set of rules when
registering:

.. code-block:: python

    from mailbot import register, Callback


    class MyCallback(Callback):

        def callback(self):
            print("Mail received for %s!" self.subject_matches[0])

    register(MyCallback, rules={'subject_patterns': [r'Hello (\w)']})


Specifying rules
----------------

Rules are regular expressions that will be tested against the various email
data:

* ``subject``: tested against the subject
* ``from``: tested against the mail sender
* ``to``: tested against each of the recipients in the "to" field
* ``cc``: tested against each of the recipients in the "cc" field
* ``bcc``: tested against each of the recipients in the "bcc" field
* ``body``: tested against the (text) body of the mail

If no rule are provided, for example for the "from" field, then no rule will be
applied, and emails from any sender will potentially trigger the callback.

For each piece of data (subject, from, to, cc, bcc, body), the callback class,
once instantiated with the mail, will have a corresponding parameter
``FOO_matches`` with all the matches from the given patterns.

Here are example subjects for the subject rules:
[``r'^Hello (\w), (.*)'``, ``r'[Hh]i (\w)!``]

* 'Hello Bryan, how are you?': ``subject_matches`` == ['Bryan', 'how are you?']
* 'Hi Bryan, how are you?': ``subject_matches`` == ['Bryan']
* 'aloha, hi Bryan!': ``subject_matches`` == ['Bryan']
* 'aloha Bryan': rules not respected, callback not triggered


How does it work?
-----------------

When an email is received on the SMTP server the MailBot is connected to
(using the IMAP protocol), it'll check all the registered callback classes and
their rules.

If each provided rule (either as a class parameter or using the register)
matches the mail's subject, from, to, cc, bcc and body, the callback class will
be instantiated, and its callback will be triggered.


Contents
--------

.. toctree::
   :maxdepth: 2
