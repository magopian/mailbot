# -*- coding: utf-8 -*-

from email import message_from_string
from imapclient import FLAGGED

from .. import register, MailBot
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
