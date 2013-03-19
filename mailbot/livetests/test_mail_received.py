# -*- coding: utf-8 -*-

from email import message_from_string
from imapclient import FLAGGED
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
            {1: {'SEQ': 1, 'RFC822': '\r\n'},
             2: {'FLAGS': ('\\Seen',), 'SEQ': 2, 'RFC822': '\r\n'}})

    def test_mark_processed(self):
        self.mb.client.append(self.home_folder,
                              message_from_string('').as_string())
        ids = self.mb.client.search(['UNDELETED'])
        self.assertEqual(ids, [1])

        self.mb.mark_processed(1)

        self.assertEquals(self.mb.client.get_flags([1]), {1: (FLAGGED,)})
        ids = self.mb.client.search(['FLAGGED'])
        self.assertEqual(ids, [1])

        ids = self.mb.client.search(['UNFLAGGED'])
        self.assertEqual(ids, [])

    def test_process_messages(self):
        # real mail
        email_file = join(dirname(dirname(__file__)),
                          'tests', 'mails', 'mail_with_attachment.txt')
        email = open(email_file, 'r').read()
        self.mb.client.append(self.home_folder, email)

        class MatchingCallback(Callback):
            """Callback with each rule matching the test mail.

            Each rule contains a non matching regexp, which shouldn't prevent
            the callback from being triggered

            """
            rules = {
                'subject': [r'Task name \w+', r'Task name (\w+)', 'NOMATCH'],
                'to': [r'\w+\+\w+@gmail.com', r'(\w+)\+(\w+)@gmail.com',
                       'NOMATCH'],
                'from': [r'\w+\.\w+@gmail.com', r'(\w+)\.(\w+)@gmail.com',
                         'NOMATCH'],
                'body': [r'Mail content \w+', r'Mail content (\w+)',
                         'NOMATCH']}

            def check_rules(self):
                res = super(MatchingCallback, self).check_rules()
                assert res, "Matching callback check_rules returned False"
                return res

            def trigger(self):
                m = self.matches['subject']
                assert len(m) == 3
                assert m[0].group(0) == 'Task name here'
                assert m[1].group(1) == 'here'
                assert m[2] is None

                m = self.matches['to']
                assert len(m) == 3
                assert m[0].group(0) == 'testmagopian+RANDOM_KEY@gmail.com'
                assert m[1].group(1) == 'testmagopian'
                assert m[1].group(2) == 'RANDOM_KEY'
                assert m[2] is None

                m = self.matches['from']
                assert len(m) == 3
                assert m[0].group(0) == 'mathieu.agopian@gmail.com'
                assert m[1].group(1) == 'mathieu'
                assert m[1].group(2) == 'agopian'
                assert m[2] is None

                m = self.matches['body']
                assert len(m) == 3
                assert m[0].group(0) == 'Mail content here'
                assert m[1].group(1) == 'here'
                assert m[2] is None

        class NonMatchingCallback(Callback):
            """Callback with each rule but one matching the test mail.

            To prevent the callback from being triggered, at least one rule
            must completely fail (have 0 regexp that matches).

            """
            rules = {  # only difference is that one rule doesn't match
                'subject': [r'Task name \w+', r'Task name (\w+)', 'NOMATCH'],
                'to': [r'\w+\+\w+@gmail.com', r'(\w+)\+(\w+)@gmail.com',
                       'NOMATCH'],
                'from': [r'\w+\.\w+@gmail.com', r'(\w+)\.(\w+)@gmail.com',
                         'NOMATCH'],
                'body': ['NOMATCH', 'DOESNT MATCH EITHER']}

            def trigger(self):
                assert False, "Non matching callback has been triggered"

        register(MatchingCallback)
        register(NonMatchingCallback)

        self.mb.process_messages()
