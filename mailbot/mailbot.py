# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
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
                 ssl=False, stream=False, timeout=None):
        """Create, connect and login the MailBot.

        All parameters except from ``timeout`` are used by IMAPClient.

        The timeout parameter is the number of seconds a mail is allowed to
        stay in the processing state.  Mails older than this timeout will have
        their processing flag removed on the next ``process_messages`` run,
        allowing MailBot to try processing them again.

        """
        self.client = self.imapclient(host, port=port, use_uid=use_uid,
                                      ssl=ssl, stream=stream)
        self.client.login(username, password)
        self.client.select_folder(self.home_folder)
        self.client.normalise_times = False  # deal with UTC everywhere
        self.timeout = timeout

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
        self.reset_timeout_messages()
        messages = self.get_messages()

        for uid, msg in messages.items():
            self.mark_processing(uid)
            message = message_from_string(msg['RFC822'])
            for callback_class, rules in CALLBACKS_MAP.items():
                self.process_message(message, callback_class, rules)
            self.mark_processed(uid)

    def reset_timeout_messages(self):
        """Remove the \\Flagged and \\Seen flags from mails that are too old.

        This makes sure that no mail stays in a processing state without
        actually being processed. This could happen if a callback timeouts,
        fails, if MailBot is killed before having finished the processing...

        """
        if self.timeout is None:
            return

        ids = self.client.search(['Flagged', 'Seen'])
        messages = self.client.fetch(ids, ['INTERNALDATE'])

        # compare datetimes without tzinfo, as UTC
        date_pivot = datetime.utcnow() - timedelta(seconds=self.timeout)
        to_reset = [msg_id for msg_id, data in messages.items()
                    if data['INTERNALDATE'].replace(tzinfo=None) < date_pivot]

        if to_reset:
            self.client.remove_flags(to_reset, ['\\Flagged', '\\Seen'])

    def mark_processing(self, uid):
        """Mark the message corresponding to uid as being processed."""
        self.client.add_flags([uid], ['\\Flagged', '\\Seen'])

    def mark_processed(self, uid):
        """Mark the message corresponding to uid as processed."""
        self.client.remove_flags([uid], ['\\Flagged'])
        self.client.add_flags([uid], ['\\Seen'])
