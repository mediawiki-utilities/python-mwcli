import os.path

from nose.tools import eq_

from ..p7z import reader
from pytest import mark


@mark.nottravis
def test_open_file():
    f = reader(os.path.join(os.path.dirname(__file__), "foo.7z"))
    eq_(f.read(), "foo\n")
