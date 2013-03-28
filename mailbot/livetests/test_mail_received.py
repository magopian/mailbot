# -*- coding: utf-8 -*-

from email import message_from_string
from os.path import dirname, join

from .. import register, MailBot, Callback
from ..tests import MailBotTestCase

try:
    import livetest_settings as settings
except ImportError:
    raise ImportError('Please create a livetest_settings.py file following '
                      'the example given here in the README ')


class MailReceivedTest(MailBotTestCase):

    def setUp(self):
        super(MailReceivedTest, self).setUp()
        self.mb = MailBot(settings.HOST, settings.USERNAME, settings.PASSWORD,
                          port=settings.PORT, use_uid=settings.USE_UID,
                          ssl=settings.SSL, stream=settings.STREAM)
        self.home_folder = '__mailbot'
        self._delete_folder()
        self.mb.client.create_folder(self.home_folder)
        self.mb.client.select_folder(self.home_folder)

    def tearDown(self):
        super(MailReceivedTest, self).tearDown()
        self._delete_folder()

    def _delete_folder(self):
        """Delete an IMAP folder, if it exists."""
        if self.mb.client.folder_exists(self.home_folder):
            self.mb.client.select_folder(self.home_folder)
            messages = self.mb.client.search('ALL')
            if messages:
                self.mb.client.remove_flags(messages,
                                            ['\\Seen', '\\Flagged'])
                self.mb.client.delete_messages(messages)
                self.mb.client.expunge()
            self.mb.client.delete_folder(self.home_folder)

    def test_get_message_ids(self):
        self.assertEqual(self.mb.get_message_ids(), [])

        self.mb.client.append(self.home_folder,
                              message_from_string('').as_string())
        self.assertEqual(self.mb.get_message_ids(), [1])

        self.mb.client.append(self.home_folder,
                              message_from_string('').as_string())
        self.assertEqual(self.mb.get_message_ids(), [1, 2])

    def test_get_messages(self):
        self.assertEqual(self.mb.get_messages(), {})

        self.mb.client.append(self.home_folder,
                              message_from_string('').as_string())
        self.assertEqual(
            self.mb.get_messages(),
            {1: {'FLAGS': ('\\Seen',), 'SEQ': 1, 'RFC822': '\r\n'}})

        self.mb.client.append(self.home_folder,
                              message_from_string('').as_string())
        self.assertEqual(
            self.mb.get_messages(),
            {2: {'FLAGS': ('\\Seen',), 'SEQ': 2, 'RFC822': '\r\n'}})

    def test_mark_processing(self):
        self.mb.client.append(self.home_folder,
                              message_from_string('').as_string())
        ids = self.mb.client.search(['Unseen'])
        self.assertEqual(ids, [1])

        self.mb.mark_processing(1)

        self.assertEquals(self.mb.client.get_flags([1]),
                          {1: ('\\Flagged', '\\Seen')})
        ids = self.mb.client.search(['Flagged', 'Seen'])
        self.assertEqual(ids, [1])

        ids = self.mb.client.search(['Unseen'])
        self.assertEqual(ids, [])
        ids = self.mb.client.search(['Unflagged'])
        self.assertEqual(ids, [])

    def test_mark_processed(self):
        self.mb.client.append(self.home_folder,
                              message_from_string('').as_string())
        ids = self.mb.client.search(['Unseen'])
        self.assertEqual(ids, [1])

        self.mb.mark_processed(1)

        self.assertEquals(self.mb.client.get_flags([1]), {1: ('\\Seen',)})
        ids = self.mb.client.search(['Seen'])
        self.assertEqual(ids, [1])

        ids = self.mb.client.search(['Flagged'])
        self.assertEqual(ids, [])

    def test_reset_timeout_messages(self):
        self.mb.timeout = -180  # 3 minutes in the future!
        self.mb.client.append(self.home_folder,
                              message_from_string('').as_string())
        ids = self.mb.client.search(['Unseen'])
        self.assertEqual(ids, [1])

        self.mb.mark_processing(1)
        self.mb.reset_timeout_messages()

        self.assertEquals(self.mb.client.get_flags([1]), {1: ()})

    def test_reset_timeout_messages_no_old_message(self):
        self.mb.timeout = 180  # 3 minutes ago
        self.mb.client.append(self.home_folder,
                              message_from_string('').as_string())
        ids = self.mb.client.search(['Unseen'])
        self.assertEqual(ids, [1])

        self.mb.mark_processing(1)
        self.mb.reset_timeout_messages()

        # reset_timeout_messages didn't reset the message
        self.assertEquals(self.mb.client.get_flags([1]),
                          {1: ('\\Flagged', '\\Seen')})

    def test_process_messages(self):
        # real mail
        email_file = join(dirname(dirname(__file__)),
                          'tests', 'mails', 'mail_with_attachment.txt')
        email = open(email_file, 'r').read()
        self.mb.client.append(self.home_folder, email)

        # Callback with each rule matching the test mail
        # Each rule contains a non matching regexp, which shouldn't prevent the
        # callback from being triggered
        matching_rules = {
            'subject': [r'Task name \w+', r'Task name (\w+)', 'NOMATCH'],
            'to': [r'\w+\+\w+@example.com', r'(\w+)\+(\w+)@example.com',
                   'NOMATCH'],
            'cc': [r'\w+@example.com', r'(\w+)@example.com', 'NOMATCH'],
            'from': [r'\w+\.\w+@example.com', r'(\w+)\.(\w+)@example.com',
                     'NOMATCH'],
            'body': [r'Mail content \w+', r'Mail content (\w+)',
                     'NOMATCH']}

        # Callback with each rule but one matching the test mail.
        # To prevent the callback from being triggered, at least one rule must
        # completely fail (have 0 regexp that matches).
        failing_rules = {
            'subject': [r'Task name \w+', r'Task name (\w+)', 'NOMATCH'],
            'to': [r'\w+\+\w+@example.com', r'(\w+)\+(\w+)@example.com',
                   'NOMATCH'],
            'cc': [r'\w+@example.com', r'(\w+)@example.com', 'NOMATCH'],
            'from': [r'\w+\.\w+@example.com', r'(\w+)\.(\w+)@example.com',
                     'NOMATCH'],
            'body': ['NOMATCH', 'DOESNT MATCH EITHER']}  # this rule fails

        class TestCallback(Callback):

            def __init__(self, message, rules):
                super(TestCallback, self).__init__(message, rules)
                self.called = False
                self.check_rules_result = False
                self.triggered = False

            def check_rules(self):
                res = super(TestCallback, self).check_rules()
                self.called = True
                self.check_rules_result = res
                return res

            def trigger(self):
                self.triggered = True

        matching_callback = TestCallback(message_from_string(email),
                                         matching_rules)

        def make_matching_callback(email, rules):
            return matching_callback

        failing_callback = TestCallback(message_from_string(email),
                                        failing_rules)

        def make_failing_callback(email, rules):
            return failing_callback

        register(make_matching_callback, matching_rules)
        register(make_failing_callback, failing_rules)

        self.mb.process_messages()

        self.assertTrue(matching_callback.called)
        self.assertTrue(matching_callback.check_rules_result)
        self.assertTrue(matching_callback.triggered)
        self.assertEqual(matching_callback.matches['subject'],
                         ['Task name here', 'here'])
        self.assertEqual(matching_callback.matches['from'],
                         ['foo.bar@example.com', ('foo', 'bar')])
        self.assertEqual(matching_callback.matches['to'],
                         ['foo+RANDOM_KEY@example.com',
                          'bar+RANDOM_KEY_2@example.com',
                          ('foo', 'RANDOM_KEY'),
                          ('bar', 'RANDOM_KEY_2')])
        self.assertEqual(matching_callback.matches['cc'],
                         ['foo@example.com',
                          'bar@example.com',
                          'foo', 'bar'])
        self.assertEqual(matching_callback.matches['body'],
                         ['Mail content here', 'here'])

        self.assertTrue(failing_callback.called)
        self.assertFalse(failing_callback.check_rules_result)
        self.assertFalse(failing_callback.triggered)
        self.assertEqual(failing_callback.matches['body'], [])
