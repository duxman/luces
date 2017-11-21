import threading
class TestThread(threading.Thread):

    def __init__(self, name='TestThread',sleepperiod=0.1):
        """ constructor, setting initial variables """
        self._stopevent = threading.Event( )
        self._sleepperiod = sleepperiod
        threading.Thread.__init__(self, name=name)

    def stop(self, timeout=None):
        """ Stop the thread and wait for it to end. """
        self._stopevent.set( )
        threading.Thread.join(self, timeout)

    def isRunning(self):
        return not self._stopevent.isSet( )