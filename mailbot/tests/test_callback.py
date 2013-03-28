# -*- coding: utf-8 -*-

from email import message_from_file, message_from_string
from os.path import dirname, join

from mock import Mock

from . import MailBotTestCase
from .. import Callback


class CallbackTest(MailBotTestCase):

    def test_init(self):
        callback = Callback('foo', 'bar')
        callback.get_email_body = lambda x: None  # mock

        self.assertEqual(callback.message, 'foo')
        self.assertEqual(callback.rules, 'bar')

    def test_check_rules(self):
        callback = Callback('foo', 'bar')
        # naive mock: return "regexps". This means that callback.matches should
        # always be the same as callback.rules
        callback.check_item = lambda x, y: y

        # no rules registered: catchall callback
        callback.rules = {}
        self.assertEqual(callback.check_rules(), True)
        self.assertEqual(callback.check_rules({}), True)

        # no rules respected
        callback.rules = {'foo': False, 'bar': [], 'baz': None}
        self.assertEqual(callback.check_rules(), False)

        # not all rules respected
        callback.rules = {'foo': True, 'bar': [], 'baz': None}
        self.assertEqual(callback.check_rules(), False)

        # all rules respected
        callback.rules = {'foo': True, 'bar': ['test'], 'baz': 'barf'}
        self.assertEqual(callback.check_rules(), True)

    def test_check_item_non_existent(self):
        empty = message_from_string('')
        callback = Callback(empty, {})

        # item does not exist
        self.assertEqual(callback.check_item('foobar', ['.*'], empty), None)
        self.assertEqual(callback.check_item('foobar', ['(.*)']), None)

    def test_check_item_subject(self):
        email_file = join(dirname(__file__), 'mails/mail_with_attachment.txt')
        email = message_from_file(open(email_file, 'r'))
        callback = Callback(email, {})

        self.assertFalse(callback.check_item('subject', []))
        self.assertEqual(callback.matches['subject'], [])

        self.assertFalse(callback.check_item('subject', ['foo']))
        self.assertEqual(callback.matches['subject'], [])

        self.assertTrue(callback.check_item('subject', ['Task name (.*)']))
        self.assertEqual(callback.matches['subject'], ['here'])

    def test_check_item_to(self):
        # "to" may be a list of several emails
        email_file = join(dirname(__file__), 'mails/mail_with_attachment.txt')
        email = message_from_file(open(email_file, 'r'))
        callback = Callback(email, {})

        self.assertTrue(callback.check_item('to', [r'\+([^@]+)@']))
        self.assertEqual(callback.matches['to'],
                         ['RANDOM_KEY', 'RANDOM_KEY_2'])

    def test_check_item_to_encoded(self):
        # "to" may be a list of several emails
        email_file = join(dirname(__file__), 'mails/mail_encoded_headers.txt')
        email = message_from_file(open(email_file, 'r'))
        callback = Callback(email, {})

        self.assertTrue(callback.check_item('to', [r'(.*) <testmagopian']))
        self.assertEqual(callback.matches['to'], [u'test création'])

    def test_check_item_body(self):
        email_file = join(dirname(__file__), 'mails/mail_with_attachment.txt')
        email = message_from_file(open(email_file, 'r'))
        callback = Callback(email, {})
        callback.get_email_body = Mock(return_value='some mail body')

        self.assertTrue(callback.check_item('body', ['.+']))
        self.assertEqual(callback.matches['body'], ['some mail body'])

    def test_get_email_body(self):
        callback = Callback('foo', 'bar')

        self.assertEqual(callback.get_email_body(), None)  # not a Message
        self.assertEqual(callback.get_email_body('foo'), None)  # not a Message

        # empty email
        empty_message = message_from_string('')
        self.assertEqual(callback.get_email_body(empty_message), '')

        # badly formed email without a 'text/plain' part
        empty_message.set_type('html/plain')
        self.assertEqual(callback.get_email_body(empty_message), '')

        # real email
        email_file = join(dirname(__file__), 'mails/mail_with_attachment.txt')
        email = message_from_file(open(email_file, 'r'))
        self.assertEqual(callback.get_email_body(email), 'Mail content here\n')

    def test_get_email_body_encoded(self):
        callback = Callback('foo', 'bar')

        # real email with encoded mail body
        email_file = join(dirname(__file__), 'mails/mail_encoded_headers.txt')
        email = message_from_file(open(email_file, 'r'))
        self.assertEqual(callback.get_email_body(email),
                         u'Test de création de bannette\n')

    def test_trigger(self):
        callback = Callback('foo', 'bar')

        self.assertRaises(NotImplementedError, callback.trigger)
