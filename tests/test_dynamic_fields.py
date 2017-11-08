from pygelf import GelfTcpHandler, GelfUdpHandler, GelfHttpHandler
from tests.helper import logger, get_unique_message, log_warning, log_exception
import pytest
import mock
import socket
import logging


class DummyFilter(logging.Filter):
    def filter(self, record):
        record.ozzy = 'diary of a madman'
        record.van_halen = 1984
        record.id = 42
        return True


@pytest.fixture(params=[
    GelfTcpHandler(host='127.0.0.1', port=12201, include_extra_fields=True),
    GelfUdpHandler(host='127.0.0.1', port=12202, include_extra_fields=True),
    GelfUdpHandler(host='127.0.0.1', port=12202, compress=False, include_extra_fields=True),
    GelfHttpHandler(host='127.0.0.1', port=12203, include_extra_fields=True),
    GelfHttpHandler(host='127.0.0.1', port=12203, compress=False, include_extra_fields=True),
])
def handler(request):
    return request.param


@pytest.yield_fixture
def logger(handler):
    logger = logging.getLogger('test')
    filter = DummyFilter()
    logger.addFilter(filter)
    logger.addHandler(handler)
    yield logger
    logger.removeHandler(handler)
    logger.removeFilter(filter)


def test_dynamic_fields(logger):
    message = get_unique_message()
    parsed_message = log_warning(logger, message, fields=['ozzy', 'van_halen'])
    assert parsed_message['message'] == message
    assert parsed_message['ozzy'] == 'diary of a madman'
    assert parsed_message['van_halen'] == 1984
    assert parsed_message['_id'] != 42
    assert 'id' not in parsed_message