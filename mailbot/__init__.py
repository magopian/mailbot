# -*- coding: utf-8 -*-

pkg_resources = __import__('pkg_resources')
distribution = pkg_resources.get_distribution('mailbot')

__version__ = distribution.version


from .callback import Callback  # noqa
from .exceptions import RegisterException  # noqa
from .mailbot import MailBot  # noqa


CALLBACKS_MAP = {}


def register(callback_class, rules=None):
    """Register a callback class, optionnally with rules."""
    if callback_class in CALLBACKS_MAP:
        raise RegisterException('%s is already registered' % callback_class)

    apply_rules = getattr(callback_class, 'rules', {})
    if rules:
        apply_rules.update(rules)
    CALLBACKS_MAP[callback_class] = apply_rules
    return apply_rules
