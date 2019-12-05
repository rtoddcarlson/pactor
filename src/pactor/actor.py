import multiprocessing


class Proxy:
    pass


class QueueRedirect:
    def __init__(self, queue, name):
        self.queue = queue
        self.name = name

    def __call__(self, *args):
        self.queue.put_nowait((self.name, args))


def actor(cls):
    def run_worker(work_queue, worker_instance):
        while True:
            task = work_queue.get()
            name = task[0]
            target = worker_instance.__getattribute__(name)

            if len(task) > 1:
                args = task[1]
                target(*args)
            else:
                target()

    class ActorProxy(object):
        def __init__(self, *args, **kwargs):
            self.manager = multiprocessing.Manager()
            self.queue = self.manager.Queue()

            actor_instance = cls(*args, **kwargs)
            self.actor_process = multiprocessing.Process(target=run_worker, args=(self.queue, actor_instance))
            self.actor_process.start()

            self.proxy = Proxy()
            for attr in cls.__dict__:
                if callable(getattr(cls, attr)) and not attr.startswith('__'):
                    setattr(self, attr, QueueRedirect(self.queue, attr))
                    setattr(self.proxy, attr, QueueRedirect(self.queue, attr))

        def join(self):
            self.actor_process.join()

    return ActorProxy
