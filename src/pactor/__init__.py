import multiprocessing

from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass


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


def actor(cls):
    """
        A class decorator used to mark a class as an Actor.
        An Actor class will run in a new process.  Instances created will be of type ActorProxy, which has a .proxy
        member that should be used for invoking any methods on the class.
    """
    close_message = '_*CLOSE*_'

    def run_worker(work_queue, worker_instance):
        """
            Runs the worker process by reading from the work_queue and executing serially.
        """
        while True:
            task = work_queue.get()  # Will block until a task is available
            name = task[0]
            if name == close_message:
                return

            target = getattr(worker_instance, name)

            if len(task) > 1:
                args = task[1]
                target(*args)
            else:
                target()

    class ActorProxy(object):
        """
            A class that builds a proxy around another class
        """
        def __init__(self, *args, **kwargs):
            # Initialize a queue that can be shared across processes
            self.manager = multiprocessing.Manager()
            self.queue = self.manager.Queue()

            # Initialize the underlying instance and process
            actor_instance = cls(*args, **kwargs)
            self.actor_process = multiprocessing.Process(target=run_worker, args=(self.queue, actor_instance))
            self.actor_process.start()

            # Build the proxy
            self.proxy = Proxy()
            setattr(self.proxy, 'act', QueueRedirect(self.queue, 'act'))
            for attr in cls.__dict__:
                if callable(getattr(cls, attr)) and not attr.startswith('__'):
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

    return ActorProxy
