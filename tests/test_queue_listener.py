import os
import subprocess
import unittest
from click.testing import CliRunner
from impulsare_config import Reader as ConfigReader
from impulsare_distributer.queue_listener import cli
base_path = os.path.abspath(os.path.dirname(__file__))


# https://docs.python.org/3/library/unittest.html#assert-methods
class TestQueueListener(unittest.TestCase):
    base_cmd = ['python', base_path + '/../impulsare_distributer/queue_listener.py']

    def test_requires_config(self):
        runner = CliRunner()
        result = runner.invoke(cli)
        self.assertIs(result.exit_code, 2)
        self.assertRegex(result.output, '.*Missing option "--host"')


    def test_bad_host(self):
        cmd = ['queue-listener', '-h', '127.0.0.1', '-p', '80', '-q', 'wrong']
        res = self._exec_cmd(cmd)
        self.assertIs(res['status'], 1, "Can't get status 1, message: {} ('{}')".format(res['stderr'], cmd))
        self.assertEqual(res['stdout'], '')
        self.assertRegex(res['stderr'], '.*Error 111 connecting to 127.0.0.1:80. Connection refused.*')
        self.assertNotRegex(res['stderr'], '.*redis.exceptions.ConnectionError: Error 111 connecting to 127.0.0.1:80. Connection refused.*')


    def test_bad_host_debug(self):
        cmd = self.base_cmd + ['--debug', '-h', '127.0.0.1', '-p', '80', '-q', 'wrong']
        res = self._exec_cmd(cmd)
        self.assertIs(res['status'], 1, "Can't get status 1, message: {} ('{}')".format(res['stderr'], cmd))
        self.assertEqual(res['stdout'], '')
        self.assertRegex(res['stderr'], '.*redis.exceptions.ConnectionError: Error 111 connecting to 127.0.0.1:80. Connection refused.*')


    def test_right_config(self):
        config = self._get_config()
        cmd = self.base_cmd + ['-h', config['distributer']['host'], '-q', config['testqueue']['queue']]
        res = self._exec_cmd(cmd)
        self.assertIs(res['status'], 0, "Can't get status 0, message: {} ('{}')".format(res['stderr'], cmd))
        self.assertEqual(res['stdout'], '')
        self.assertRegex(res['stderr'], '.*RQ worker.*started')


    def _get_config(self):
        config_specs = base_path + '/../impulsare_distributer/static/specs.yml'
        config_default = base_path + '/../impulsare_distributer/static/default.yml'

        config_file = base_path + '/static/config_valid.yml'
        # Use another server, make sure to have the right configuration file
        if 'REDIS' in os.environ and os.environ['REDIS'] != '127.0.0.1':
            config_file = base_path + '/static/config_valid_{}.yml'.format(os.environ['REDIS'])

        config = ConfigReader().parse(config_file, config_specs, config_default)

        return config


    def _exec_cmd(self, cmd: list):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            stdout, stderr = p.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            p.terminate()
            stdout, stderr = p.communicate()

        stdout = stdout.decode().strip().replace('\n', '')
        stderr = stderr.decode().strip().replace('\n', '')

        return {'stdout': stdout, 'stderr': stderr, 'status': p.returncode}
