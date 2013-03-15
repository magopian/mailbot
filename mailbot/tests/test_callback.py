# -*- coding: utf-8 -*-

from . import MailBotTestCase
from .. import Callback


class CallbackTest(MailBotTestCase):

    def test_init(self):
        callback = Callback('foo', 'bar')
        self.assertEqual(callback.message, 'foo')
        self.assertEqual(callback.rules, 'bar')

    def test_check_rules(self):
        callback = Callback('foo', 'bar')
        self.assertEqual(callback.check_rules(), False)
