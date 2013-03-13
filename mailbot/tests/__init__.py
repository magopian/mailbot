# -*- coding: utf-8 -*-

from unittest2 import TestCase

from .. import CALLBACKS_MAP


class MailBotTestCase(TestCase):
    """TestCase that restores the CALLBACKS_MAP after each test run."""

    def setUp(self):
        self.callbacks_map_save = CALLBACKS_MAP.copy()

    def tearDown(self):
        CALLBACKS_MAP = self.callbacks_map_save  # noqa
