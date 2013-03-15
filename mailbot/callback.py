# -*- coding: utf-8 -*-


class Callback(object):
    """Base class for callbacks."""

    def __init__(self, message, rules):
        self.message = message
        self.rules = rules

    def check_rules(self):
        """Does this message conform to the rules provided?"""
        raise NotImplementedError
