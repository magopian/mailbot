# -*- coding: utf-8 -*-

from email import message_from_string

from imapclient import IMAPClient


class MailBot(object):
    """MailBot mail class, where the magic is happening.

    Connect to the SMTP server using the IMAP protocol, for each unflagged
    message check which callbacks should be triggered, if any, but testing
    against the registered rules for each of them.

    """
    home_folder = 'INBOX'
    imapclient = IMAPClient

    def __init__(self, host, username, password, port=None, use_uid=True,
                 ssl=False, stream=False):
        self.client = self.imapclient(host, port=port, use_uid=use_uid,
                                      ssl=ssl, stream=stream)
        self.client.login(username, password)
        self.client.select_folder(self.home_folder)

    def get_message_ids(self):
        """Return the list of IDs of messages to process."""
        return self.client.search(['Unseen', 'Unflagged'])

    def get_messages(self):
        """Return the list of messages to process."""
        ids = self.get_message_ids()
        return self.client.fetch(ids, ['RFC822'])

    def process_message(self, message, callback_class, rules):
        """Check if callback matches rules, and if so, trigger."""
        callback = callback_class(message, rules)
        if callback.check_rules():
            return callback.trigger()

    def process_messages(self):
        """Process messages: check which callbacks should be triggered."""
        from . import CALLBACKS_MAP
        messages = self.get_messages()

        for uid, msg in messages.items():
            self.mark_processing(uid)
            message = message_from_string(msg['RFC822'])
            for callback_class, rules in CALLBACKS_MAP.items():
                self.process_message(message, callback_class, rules)
            self.mark_processed(uid)

    def mark_processing(self, uid):
        """Mark the message corresponding to uid as being processed."""
        self.client.add_flags([uid], ['\\Flagged', '\\Seen'])

    def mark_processed(self, uid):
        """Mark the message corresponding to uid as processed."""
        self.client.remove_flags([uid], ['\\Flagged'])
        self.client.add_flags([uid], ['\\Seen'])
