import pytest
from NumberParser import NumberParser

@pytest.fixture
def numberParser():
    numberParser = NumberParser()
    return numberParser


def test_ordinal_number(numberParser):
	assert numberParser.parse('forth') == 4
	assert numberParser.parse('Eleventh') == 11
	assert numberParser.parse('Eleventh') == 11