# -*- coding: utf-8 -*-

from re import search


class Callback(object):
    """Base class for callbacks."""
    matches = {}

    def __init__(self, message, rules):
        self.message = message
        self.rules = rules

    def check_rules(self, rules=None):
        """Does this message conform to the all the rules provided?

        For each item in the rules dictionnary (item, [regexp1, regexp2...]),
        call ``self.check_item``.

        """
        if rules is None:
            rules = self.rules

        if not rules:  # if no (or empty) rules, it's a catchall callback
            return True

        rules_tests = [self.check_item(item, regexps)
                       for item, regexps in rules.iteritems()]

        return all(rules_tests)  # True only if at least one value is

    def check_item(self, item, regexps, message=None):
        """Search the email's item using the given regular expressions.

        Item is one of subject, from, to, cc, body.

        Store the result of searching the item with the regular expressions in
        self.matches[item]. If the search doesn't match anything, this will
        result in a None, otherwise it'll be a ``re.MatchObject``.

        """
        if message is None:
            message = self.message

        if item not in message and item != 'body':  # bad item, not found
            return None

        # if item is not in header, then item == 'body'
        value = message.get(item, self.get_email_body(message))

        self.matches[item] = [search(regexp, value) for regexp in regexps]

        return any(self.matches[item])

    def get_email_body(self, message=None):
        """Return the message text body.

        Return the first 'text/plain' part of the email.Message that doesn't
        have a filename.

        """
        if message is None:
            message = self.message

        if not hasattr(message, 'walk'):  # not an email.Message instance?
            return None

        for part in message.walk():
            content_type = part.get_content_type()
            filename = part.get_filename()
            if content_type == 'text/plain' and filename is None:
                # text body of the mail, not an attachment
                return part.get_payload()
        return ''

    def trigger(self):
        """Called when a mail matching the registered rules is received."""
        raise NotImplementedError("Must be implemented in a child class.")
