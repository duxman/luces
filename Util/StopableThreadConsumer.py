import Queue
import threading

import PinManager


class Consumer(threading.Thread):
    ConsumerQueue = None
    def __init__(self, queue = None,target = None, sleep = 0.1, name = "DefaultConsumerThread"):
        """
        :param queue: Cola de mensajes de donde obtendremos los datos a procesar
        :param target: Funcion a ejecutar para procesar los datos
        :param sleep: Tiempo de parada entre mensaje y mensaje
        :param name: Nombre identificativo del thread consumidor
        """
        """ constructor, setting initial variables """
        self.ConsumerQueue = queue
        self.Target = target
        self.Name = name
        self.SleepPeriod = sleep

        """ Creamos el Evento de parada y el tiempo de espera"""
        self._stopevent = threading.Event( )
        self._sleepperiod = self.SleepPeriod
        """Creamos el thread desde el padre"""
        threading.Thread.__init__(self, name=self.Name)

    def stop(self, timeout=1):
        """
        Paramaos el thread
        :param timeout: timeout de espera para para el thread
        :return: None
        """
        """ Stop the thread and wait for it to end. """
        self._stopevent.set( )
        """Esperamos el tiempo fijado de parada"""
        threading.Thread.join(self, timeout)


    def isRunning(self):
        """
        Comprobamos si el thread esta en ejecucion
        :return:
        """
        return not self._stopevent.isSet( )

    def run(self):
        """
        Funcion de ejecucion del thread
        :return:
        """
        #print "%s
        #  starts" % (self.getName(),)
        #count = 0
        """Mientras no este parado"""
        while self.isRunning():
            try:
                """"Obtenemos el valor de la cola esperamos si esta relleno"""
                valor = self.ConsumerQueue.get( False, self._sleepperiod)
                """comprobamos si tenemos target si no lo tenemos """
                if self.Target == None:
                    print "Loop %d Valor %s" % (count, valor,)
                else:
                    """Si tenemos target pasamos el valor al controlador"""
                    self.Target(valor)
                """Comprobamos si tenemos que esperar"""
                if(self._sleepperiod > 0):
                    """Hacemos un wait con tiempo para no quedarnos bloqueados"""
                    self._stopevent.wait(self._sleepperiod)
                """indicamos la finalizacion del proceso del valor para que lo elimine de la queue"""
                self.ConsumerQueue.task_done()

            except Queue.Empty as e:
                """si no tenemos valor lo controlamos"""
                pass
                #print "Empty...  " + e.message
        """Fin del proceso"""
        print "%s ends" % (self.getName(),)




if __name__ == "__main__":
    q = Queue.Queue()
    pinman = PinManager.PinManager(None, [2, 3, 4, 17, 27, 22, 10, 9, 11, 5])

    testthread = Consumer( q,target =pinman.EncenderInRange, name="MiConsumidor" )
    testthread.start( )

    producer = threading.Thread(target=PlayWavFile("music/sample3.wav",queue=q))
    producer.start()
    q.join()
    #producer.join()

    print "fin"
    testthread.stop(timeout=0.3 )
    print "finStop"

    print str ( producer.is_alive() )

