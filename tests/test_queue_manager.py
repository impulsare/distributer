import unittest
import os
import redis
import sys

from impulsare_config import Reader
from redis.exceptions import ConnectionError

from impulsare_distributer import QueueManager
base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(base_dir + '/../'))


def fake_print(message: str, job: str):
    print('Message: {}'.format(message))
    print('Job: {}'.format(job))


# https://docs.python.org/3/library/unittest.html#assert-methods
class TestQueueManager(unittest.TestCase):
    def test_init_queue_invalid_conf(self):
        with self.assertRaisesRegex(ValueError, "Your config is not valid: 'host' is a required property"):
            QueueManager(base_dir + '/static/config_invalid.yml', 'testqueue')


    def test_init_queue_missing_subkey_queue(self):
        with self.assertRaisesRegex(KeyError, "You must have a key testqueue in your config with a sub-key queue"):
            QueueManager(base_dir + '/static/config_missing_queue.yml', 'testqueue')


    def test_queue_invalid_server(self):
        with self.assertRaisesRegex(ConnectionError, "Error.*connecting to abc:6379.*"):
            q = QueueManager(base_dir + '/static/config_wrong_server.yml', 'testqueue')
            q.add('Hello world', fake_print, 'test')


    def test_queue_valid(self):
        config_file = base_dir + '/static/config_valid.yml'
        specs_file = base_dir + '/../impulsare_distributer/static/specs.yml'
        config = Reader().parse(config_file, specs_file).get('distributer')
        host = config['host']
        if os.getenv('REDIS') is not None:
            host = os.getenv('REDIS')
        con = redis.StrictRedis(host=host)

        # Clean
        items = con.keys('rq:*')
        for item in items:
            con.delete(item)
        items = con.keys('rq:*')
        self.assertEqual(len(items), 0)

        try:
            q = QueueManager(config_file, 'testqueue')
            job = q.add('Hello world', fake_print, 'test')
        except ConnectionError:
            print('Be careful to set the right server in config_valid')
            sys.exit(0)

        items = con.keys('rq:*')
        self.assertGreater(len(items), 0)
        self.assertIn(b'rq:queues', items)
        self.assertIn(b'rq:job:' + job.id.encode(), items)
