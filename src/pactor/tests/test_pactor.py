from unittest import TestCase, mock
from pactor.tests import actor_test_context


class SampleActor:
    def one(self):
        return 1

    def two(self):
        return 2

    def three(self):
        return 3


class PactorTests(TestCase):
    def test_actor_creates_proxy(self):
        """ Validates that an @actor proxy has the correct methods """
        with actor_test_context(SampleActor()) as context:
            self.assertIsNotNone(context.actor.proxy)
            self.assertTrue(callable(context.actor.proxy.one))
            self.assertTrue(callable(context.actor.proxy.two))
            self.assertTrue(callable(context.actor.proxy.three))

    def test_actor_starts_process(self):
        """ Validates that an @actor starts a process """
        with actor_test_context(SampleActor()) as context:
            context.process.assert_has_calls([mock.call().start()])

    def test_actor_join_joins_process(self):
        """ Validates that calling join() on an @actor joins the process """
        with actor_test_context(SampleActor()) as context:
            context.actor.join()
            context.process.assert_has_calls([mock.call().join()])

    def test_actor_close_writes_to_queue(self):
        """ Validates that calling close() on an @actor writes the close message to the queue """
        with actor_test_context(SampleActor()) as context:
            context.actor.close()
            context.queue.assert_has_calls([mock.call.put_nowait(('_*CLOSE*_',))])

    def test_actor_proxy_method_writes_to_queue(self):
        """ Validates that calling an @actor method writes to the queue """
        with actor_test_context(SampleActor()) as context:
            context.actor.proxy.one()
            context.queue.assert_has_calls([mock.call.put_nowait(('one', ()))])

    def test_actor_proxy_method_writes_to_queue_with_argument(self):
        """ Validates that calling an @actor method with an argument writes to the queue """
        with actor_test_context(SampleActor()) as context:
            context.actor.proxy.one(101)
            context.queue.assert_has_calls([mock.call.put_nowait(('one', (101,)))])

    def test_actor_proxy_method_writes_to_queue_with_multiple_arguments(self):
        """ Validates that calling an @actor method with multiple arguments writes to the queue """
        with actor_test_context(SampleActor()) as context:
            context.actor.proxy.one(101, 'a', 102)
            context.queue.assert_has_calls([mock.call.put_nowait(('one', (101, 'a', 102)))])
