import multiprocessing

from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass


close_message = '_*CLOSE*_'


class ActorWrapper:
    """
        A class that builds a proxy around another class
    """
    def __init__(self, actor_instance):
        # Initialize a queue that can be shared across processes
        self.manager = multiprocessing.Manager()
        self.queue = self.manager.Queue()

        # Initialize the underlying instance and process
        setattr(actor_instance, 'enqueue', EnqueueCall(self.queue))
        self.actor_process = multiprocessing.Process(target=run_actor, args=(self.queue, actor_instance))
        self.actor_process.start()

        # Build the proxy
        self.proxy = Proxy()
        for attr in dir(actor_instance.__class__):
            if callable(getattr(actor_instance, attr)) and not attr.startswith('__'):
                setattr(self, attr, QueueRedirect(self.queue, attr))
                setattr(self.proxy, attr, QueueRedirect(self.queue, attr))

    def join(self):
        """
            Join the calling thread to the process for the actor.
        """
        self.actor_process.join()

    def close(self):
        """
            Close the processing queue for the actor.
        """
        self.queue.put_nowait((close_message,))


class Proxy:
    """
        An empty class to be used for building a proxy for another class by directly setting attributes to match
        the other class.
    """
    pass


class QueueRedirect:
    """
        A callable that writes to a queue.  The tuple value written to the queue includes the name specified
        when creating the QueueRedirect as well as the arguments passed to the call.
    """

    def __init__(self, queue, name):
        self.queue = queue
        self.name = name

    def __call__(self, *args):
        self.queue.put_nowait((self.name, args))


class EnqueueCall:
    """
        A callable that writes to a queue from a callable target.  The tuple value written to the queue includes the
        name of the callable_target as well as the arguments passed to the call.
    """
    def __init__(self, queue):
        self.queue = queue

    def __call__(self, callable_target, *args):
        self.queue.put_nowait((callable_target.__name__, args))


def run_actor(actor_queue, actor_instance):
    """
        Runs the worker process by reading from the work_queue and executing serially.
    """
    while True:
        task = actor_queue.get()  # Will block until a task is available
        name = task[0]
        if name == close_message:
            return

        target = getattr(actor_instance, name)

        if len(task) > 1:
            args = task[1]
            target(*args)
        else:
            target()
