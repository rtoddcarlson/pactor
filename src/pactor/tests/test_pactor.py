from unittest import TestCase, mock
from unittest.mock import MagicMock

from pactor.tests import actor_test_context


class SampleActor:
    def __init__(self):
        self.one_called = False
        self.two_called = False
        self.name = None
        self.value = None

    def one(self):
        self.one_called = True
        return 1

    def two(self, name, value):
        self.two_called = True
        self.name = name
        self.value = value


class PactorTests(TestCase):
    def test_actor_creates_proxy(self):
        """ Validates that an actor proxy has the correct methods """
        with actor_test_context(SampleActor()) as context:
            self.assertIsNotNone(context.actor.proxy)
            self.assertTrue(callable(context.actor.proxy.one))
            self.assertTrue(callable(context.actor.proxy.two))

    def test_actor_starts_process(self):
        """ Validates that an actor starts a process """
        with actor_test_context(SampleActor()) as context:
            context.process.assert_has_calls([mock.call().start()])

    def test_actor_join_joins_process(self):
        """ Validates that calling join() on an actor joins the process """
        with actor_test_context(SampleActor()) as context:
            context.actor.join()
            context.process.assert_has_calls([mock.call().join()])

    def test_actor_close_writes_to_queue(self):
        """ Validates that calling close() on an actor writes the close message to the queue """
        with actor_test_context(SampleActor()) as context:
            context.actor.close()
            context.queue.assert_has_calls([mock.call.put_nowait(('_*CLOSE*_',))])

    def test_actor_proxy_method_writes_to_queue(self):
        """ Validates that calling an actor proxy method writes to the queue """
        with actor_test_context(SampleActor()) as context:
            context.actor.proxy.one()
            context.queue.assert_has_calls([mock.call.put_nowait(('one', ()))])

    def test_actor_proxy_method_writes_to_queue_with_argument(self):
        """ Validates that calling an actor proxy method with an argument writes to the queue """
        with actor_test_context(SampleActor()) as context:
            context.actor.proxy.one(101)
            context.queue.assert_has_calls([mock.call.put_nowait(('one', (101,)))])

    def test_actor_proxy_method_writes_to_queue_with_multiple_arguments(self):
        """ Validates that calling an actor proxy method with multiple arguments writes to the queue """
        with actor_test_context(SampleActor()) as context:
            context.actor.proxy.one(101, 'a', 102)
            context.queue.assert_has_calls([mock.call.put_nowait(('one', (101, 'a', 102)))])

    def test_actor_enqueue_method_writes_to_queue(self):
        """ Validates that enqueue on an actor instance writes to the queue """
        sample = SampleActor()
        with actor_test_context(sample) as context:
            sample.enqueue(sample.one)
            context.queue.assert_has_calls([mock.call.put_nowait(('one', ()))])

    def test_run_actor_close_prevents_further_queue_reads(self):
        """ Validates that the close message prevents further reads from the queue """
        sample = SampleActor()
        with actor_test_context(sample) as context:
            get_sequence = MagicMock()
            get_sequence.side_effect = [(context.actor.__close_message__, )]
            context.queue.get = get_sequence
            context.actor.__run_actor__(context.queue, sample)

            context.queue.assert_has_calls([mock.call.get()])

    def test_run_actor_calls_instance_method(self):
        """ Validates that a queue message correctly calls a method without arguments """
        sample = SampleActor()
        with actor_test_context(sample) as context:
            get_sequence = MagicMock()
            get_sequence.side_effect = [('one',), (context.actor.__close_message__, )]
            context.queue.get = get_sequence
            context.actor.__run_actor__(context.queue, sample)
            self.assertTrue(sample.one_called)

    def test_run_actor_calls_instance_method_with_arguments(self):
        """ Validates that a queue message correctly calls a method with arguments """
        sample = SampleActor()
        with actor_test_context(sample) as context:
            get_sequence = MagicMock()
            get_sequence.side_effect = [('two', ('test_name', 99)), (context.actor.__close_message__, )]
            context.queue.get = get_sequence
            context.actor.__run_actor__(context.queue, sample)

            self.assertTrue(sample.two_called)
            self.assertEqual('test_name', sample.name)
            self.assertEqual(99, sample.value)
