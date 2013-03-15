# -*- coding: utf-8 -*-

from . import MailBotTestCase
from .. import register, CALLBACKS_MAP, RegisterException


class RegisterTest(MailBotTestCase):

    def setUp(self):
        super(RegisterTest, self).setUp()

        class EmptyCallback(object):
            pass

        class WithRulesCallback(object):
            rules = {'foo': 'bar', 'baz': 'bat'}

        self.empty_callback = EmptyCallback
        self.with_rules_callback = WithRulesCallback

    def test_register(self):
        before = len(CALLBACKS_MAP)
        register(self.empty_callback)
        self.assertEqual(len(CALLBACKS_MAP), before + 1)

    def test_register_existing(self):
        register(self.empty_callback)
        self.assertRaises(RegisterException, register, self.empty_callback)
        self.assertTrue(register(self.with_rules_callback))

    def test_register_without_rules_callback_with_rules(self):
        register(self.with_rules_callback)
        self.assertEqual(CALLBACKS_MAP[self.with_rules_callback],
                         self.with_rules_callback.rules)

    def test_register_with_rules_callback_without_rules(self):
        register(self.empty_callback, {'one': 'two'})
        self.assertEqual(CALLBACKS_MAP[self.empty_callback], {'one': 'two'})

    def test_register_with_rules_callback_with_rules(self):
        register(self.with_rules_callback, {'baz': 'wow'})
        self.assertEqual(CALLBACKS_MAP[self.with_rules_callback],
                         {'foo': 'bar', 'baz': 'wow'})
