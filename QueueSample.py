import contextlib
import wave
import audioop
import pyaudio
import threading
import Queue
from datetime import datetime

class parameters(object):
    pass

class Consumer(threading.Thread):
    ConsumerQueue = None
    def __init__(self, queue, **attrs):
        self.ConsumerQueue = queue
        e = parameters()

        for k, v in attrs.iteritems():
            setattr(e, k, v)
        self.Target = getattr(e, "target", None)
        self.Name = getattr(e, "name", 'DefaultConsumer')
        self.SleepPeriod = getattr(e, "sleep", 0)

        """ constructor, setting initial variables """
        self._stopevent = threading.Event( )
        self._sleepperiod = self.SleepPeriod

        threading.Thread.__init__(self, name=self.Name)

    def stop(self, timeout=None):
        """ Stop the thread and wait for it to end. """
        self._stopevent.set( )
        threading.Thread.join(self, timeout)


    def isRunning(self):
        return not self._stopevent.isSet( )

    def run(self):
        print "%s starts" % (self.getName(),)
        count = 0
        while self.isRunning():
            try:
                valor = self.ConsumerQueue.get( False, self._sleepperiod)
                count += 1
                if self.Target == None:
                    print "Loop %d Valor %s" % (count, valor,)
                else:
                    self.Target(valor)

                if(self._sleepperiod > 0):
                    self._stopevent.wait(self._sleepperiod)
                self.ConsumerQueue.task_done()

            except Queue.Empty as e:
                pass
                #print "Empty...  " + e.message

        print "%s ends" % (self.getName(),)


def PlayWavFile(FileName, **attrs):
    e = parameters()
    for k, v in attrs.iteritems():
        setattr(e, k, v)
    ValorTiempo = getattr(e, "tiempo", 250)
    ValorQueue = getattr(e, "queue", None )
    with contextlib.closing(wave.open(FileName, 'rb')) as analizer:
        periodsize = analizer.getframerate() / 8
        max = audioop.rms( analizer.readframes( -1 ) , 2)

    with contextlib.closing(wave.open(FileName, 'rb')) as f:
        rate = (f.getframerate() / ValorTiempo) / 2
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                        channels=f.getnchannels(),
                        rate=f.getframerate(),
                        output=True)

        data = f.readframes(rate + 1)

        i = 0
        while data:
            i = i + 1
            valor = int(round( audioop.rms(data, 2) * 5 / max ))
            queuevalue =  ''.ljust(valor * 2, "#")
            ValorQueue.put( queuevalue )
            stream.write(data)
            data = f.readframes(rate + 1)

        ValorQueue.join()
        stream.stop_stream()
        stream.close()
        p.terminate()

class targetclass():
    array = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    def printfunction(self, valor):
        a,b,c,d,self.array[:valor]
        #print "Target value %s" % (valor,)
        print(arr)

if __name__ == "__main__":
    q = Queue.Queue()
    c = targetclass();
    testthread = Consumer( q,target =c.printfunction, name="MiConsumidor" )
    testthread.start( )

    producer = threading.Thread(target=PlayWavFile("music/sample2.wav",queue=q))
    producer.start()
    q.join()
    #producer.join()

    print "fin"
    testthread.stop(timeout=0.3 )
    print "finStop"

    print str ( producer.is_alive() )

