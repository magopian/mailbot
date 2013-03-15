# -*- coding: utf-8 -*-

from mock import patch, sentinel, Mock, DEFAULT, call

from . import MailBotTestCase
from .. import CALLBACKS_MAP, MailBot


class TestableMailBot(MailBot):

    def __init__(self, *args, **kwargs):
        self.client = Mock()


class MailBotClientTest(MailBotTestCase):

    def setUp(self):
        super(MailBotClientTest, self).setUp()
        self.bot = TestableMailBot('somehost', 'john', 'doe')


class MailBotTest(MailBotClientTest):

    @patch.multiple('imapclient.imapclient.IMAPClient',
                    login=DEFAULT, __init__=DEFAULT)
    def test_init(self, login, __init__):
        __init__.return_value = None

        kwargs = {'port': sentinel.port,
                  'ssl': sentinel.ssl,
                  'use_uid': sentinel.use_uid,
                  'stream': sentinel.use_stream}
        MailBot('somehost', 'john', 'doe', **kwargs)

        __init__.assert_called_once_with('somehost', **kwargs)
        login.assert_called_once_with('john', 'doe')

    def test_get_message_ids(self):
        self.bot.client.search.return_value = sentinel.id_list

        res = self.bot.get_message_ids()

        self.bot.client.search.assert_called_once_with(['UNFLAGGED'])
        self.assertEqual(res, sentinel.id_list)

    def test_get_messages(self):
        self.bot.get_message_ids = Mock(return_value=sentinel.ids)
        self.bot.client.fetch.return_value = sentinel.message_list

        messages = self.bot.get_messages()

        self.bot.get_message_ids.assert_called_once_with()
        self.bot.client.fetch.assert_called_once_with(sentinel.ids, ['RFC822'])
        self.assertEqual(messages, sentinel.message_list)

    def test_process_message_trigger(self):
        callback = Mock()
        callback.check_rules.return_value = True
        callback.callback.return_value = sentinel.callback_result
        callback_class = Mock(return_value=callback)

        res = self.bot.process_message(sentinel.message, callback_class,
                                       sentinel.rules)

        callback_class.assert_called_once_with(sentinel.message,
                                               sentinel.rules)
        callback.check_rules.assert_called_once_with()
        callback.callback.assert_called_once_with()
        self.assertEqual(res, sentinel.callback_result)

    def test_process_message_no_trigger(self):
        callback = Mock()
        callback.check_rules.return_value = False
        callback_class = Mock(return_value=callback)

        res = self.bot.process_message(sentinel.message, callback_class,
                                       sentinel.rules)

        callback.check_rules.assert_called_once_with()
        self.assertEqual(res, None)

    def test_process_messages(self):
        messages = {1: {'RFC822': sentinel.mail1},
                    2: {'RFC822': sentinel.mail2}}
        self.bot.get_messages = Mock(return_value=messages)
        # message constructor will return exactly what it's given
        # to be used in the "self.bot.process_message.assert_has_calls" below
        self.bot.message_constructor = Mock(side_effect=lambda m: m)
        self.bot.process_message = Mock()
        self.bot.mark_processed = Mock()
        CALLBACKS_MAP.update({sentinel.callback1: sentinel.rules1,
                             sentinel.callback2: sentinel.rules2})

        self.bot.process_messages()

        self.bot.get_messages.assert_called_once_with()
        self.bot.process_message.assert_has_calls(
            [call(sentinel.mail1, sentinel.callback1, sentinel.rules1),
             call(sentinel.mail2, sentinel.callback1, sentinel.rules1),
             call(sentinel.mail1, sentinel.callback2, sentinel.rules2),
             call(sentinel.mail2, sentinel.callback2, sentinel.rules2)],
            any_order=True)

    def test_mark_processed(self):
        self.bot.mark_processed(sentinel.id)
        self.bot.client.set_flags.assert_called_once_with([sentinel.id],
                                                          ['FLAGGED'])
