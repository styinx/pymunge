from pathlib import Path
from unittest import TestCase

from source.pymunge.swbf.parsers.odf import Odf
from source.pymunge.app.registry import FileRegistry


class OdfTest(TestCase):

    def test_init(self):
        odf = Odf(FileRegistry(), Path(''))

        self.assertTrue(odf)
