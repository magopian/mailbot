# -*- coding: utf-8 -*-

from email import message_from_file, message_from_string
from os import path
from re import search

from mock import sentinel, Mock

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

    def test_check_item(self):
        empty = message_from_string('')
        callback = Callback(empty, {})

        # item does not exist
        self.assertEqual(callback.check_item('foobar', ['.*'], empty), None)
        self.assertEqual(callback.check_item('foobar', ['(.*)']), None)

        # test on real mail
        email_file = path.join(path.dirname(__file__),
                               'mails/mail_with_attachment.txt')
        email = message_from_file(open(email_file, 'r'))
        callback = Callback(email, {})

        # subject
        self.assertFalse(callback.check_item('subject', []))
        self.assertEqual(callback.matches['subject'], [])

        self.assertTrue(callback.check_item('subject', ['(.*)']))
        self.assertEqual(callback.matches['subject'][0].groups(),
                         search('(.*)', 'Task name here').groups())

        # body
        callback.get_email_body = Mock(return_value='some mail body')
        self.assertFalse(callback.check_item('body', []))
        self.assertEqual(callback.matches['body'], [])
        callback.get_email_body.assert_called_once_with(email)

        self.assertTrue(callback.check_item('body', ['(.*)']))
        self.assertEqual(callback.matches['body'][0].groups(),
                         search('(.*)', 'some mail body').groups())

    def test_get_email_body(self):
        callback = Callback('foo', 'bar')

        self.assertEqual(callback.get_email_body(), None)  # not a Message
        self.assertEqual(callback.get_email_body('foo'), None)  # not a Message

        empty_message = message_from_string('')
        self.assertEqual(callback.get_email_body(empty_message), '')

        email_file = path.join(path.dirname(__file__),
                               'mails/mail_with_attachment.txt')
        email = message_from_file(open(email_file, 'r'))
        self.assertEqual(callback.get_email_body(email), 'Mail content here\n')
