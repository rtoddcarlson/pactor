import multiprocessing

from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass


close_message = '_*CLOSE*_'


class Actor:
    """
        Wraps a pickleable class as an actor to run in a dedicated process.
        The returned Actor instance has a .proxy attribute that should be used
        to invoke the methods of the wrapped class.
    """
    def __init__(self, actor_instance):
        # Initialize a queue that can be shared across processes
        manager = multiprocessing.Manager()
        self.queue = manager.Queue()

        # Initialize the underlying instance and process
        setattr(actor_instance, 'enqueue', EnqueueDirectCall(self.queue))
        self.actor_process = multiprocessing.Process(target=self.__run_actor__, args=(self.queue, actor_instance))
        self.actor_process.start()

        # Build the proxy
        self.proxy = Proxy()
        for attr in dir(actor_instance.__class__):
            if callable(getattr(actor_instance, attr)) and not attr.startswith('__'):
                setattr(self.proxy, attr, EnqueueNamedCall(self.queue, attr))

    def close(self):
        """ Closes the actor process """
        self.queue.put_nowait((close_message,))

    def join(self):
        """ Joins the calling thread to the process for the actor. """
        self.actor_process.join()

    @staticmethod
    def __run_actor__(queue, actor_instance):
        """ Runs the actor process by reading from the queue and executing serially. """
        while True:
            task = queue.get()  # Will block until a task is available
            name = task[0]
            if name == close_message:
                return

            target = getattr(actor_instance, name)

            if len(task) > 1:
                args = task[1]
                target(*args)
            else:
                target()


class Proxy:
    """ An empty class definition used to create a proxy for an Actor """
    pass


class EnqueueNamedCall:
    """
        A callable that writes to a queue.  The tuple value written to the queue includes the name specified
        when creating the QueueRedirect as well as the arguments passed to the call.
    """
    def __init__(self, queue, name):
        self.queue = queue
        self.name = name

    def __call__(self, *args):
        self.queue.put_nowait((self.name, args))


class EnqueueDirectCall:
    """
        A callable that writes to a queue from a callable target.  The tuple value written to the queue includes the
        name of the callable_target as well as the arguments passed to the call.
    """
    def __init__(self, queue):
        self.queue = queue

    def __call__(self, callable_target, *args):
        self.queue.put_nowait((callable_target.__name__, args))
