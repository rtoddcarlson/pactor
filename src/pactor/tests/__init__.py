from contextlib import contextmanager
from unittest.mock import patch, MagicMock
from pactor import actor


class ActorTestContext:
    def __init__(self, test_actor, mock_process, mock_manager, mock_queue):
        self.actor = test_actor
        self.process = mock_process
        self.manager = mock_manager
        self.queue = mock_queue


@contextmanager
def actor_test_context(actor_cls):
    with patch('multiprocessing.Manager') as mock_manager:
        with patch('multiprocessing.Process') as mock_process:
            queue = MagicMock()
            mock_manager().Queue = MagicMock(return_value=queue)
            test_actor = actor(actor_cls)()
            yield ActorTestContext(test_actor, mock_process, mock_manager, queue)
