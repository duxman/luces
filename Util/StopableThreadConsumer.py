import Queue
import threading

import PinManager


class StopableConsumerThread(threading.Thread):
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
        while self.isRunning() and self.Target != None:
            if  self.ConsumerQueue !=None:

                try:
                    """"Obtenemos el valor de la cola esperamos si esta relleno"""
                    valor = self.ConsumerQueue.get( False, self._sleepperiod)

                    self.Target(valor)

                    """indicamos la finalizacion del proceso del valor para que lo elimine de la queue"""
                    self.ConsumerQueue.task_done()
                except Queue.Empty:
                    """si no tenemos valor lo controlamos"""
                    pass
                    #print "Empty...  " + e.message
            else:
                """comprobamos si tenemos target si no lo tenemos """
                self.Target(valor)

            """Comprobamos si tenemos que esperar"""
            if (self._sleepperiod > 0):
                """Hacemos un wait con tiempo para no quedarnos bloqueados"""
                self._stopevent.wait(self._sleepperiod)

        """Fin del proceso"""
        print "%s ends" % (self.getName(),)

