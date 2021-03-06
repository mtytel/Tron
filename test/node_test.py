import os
import tempfile
import shutil

from testify import *
from testify.utils import turtle

from tron import node, action, job
from tron.utils.testingutils import run_reactor

class NodeTestCase(TestCase):
    class TestConnection(object):
        def openChannel(self, chan):
            self.chan = chan

    @setup
    def setup(self):
        self.test_dir = tempfile.mkdtemp()

    @teardown
    def teardown(self):
        shutil.rmtree(self.test_dir)

    def test_output_logging(self):
        act = action.Action(name="Test Action")
        act.command = "echo Hello"
        jo = job.Job("Test Job", act)
        jo.output_dir = self.test_dir
        jo.node_pool = turtle.Turtle()
        act.job = jo

        run = jo.build_run()
        nod = node.Node(hostname="localhost")
        act_run = run.runs[0]
        act_run.stdout_file = tempfile.TemporaryFile('w+b')
        
        nod.connection = self.TestConnection()
        nod.run_states = {act_run.id:turtle.Turtle(state=0)}
        nod.run_states[act_run.id].state = node.RUN_STATE_CONNECTING

        nod._open_channel(act_run)
        assert not nod.connection.chan is None
        nod.connection.chan.dataReceived("test")

        act_run.stdout_file.seek(0)
        assert act_run.stdout_file.read(4) == "test"
        act_run.stdout_file.close()


if __name__ == '__main__':
    run()
