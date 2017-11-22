import pprint


def my_callback_func(event, valor):
    print "hola " + valor
    print(event.__dict__)

class Event(object):
    pass

class Observable(object):
    callbacks = None

    def __init__(self):
        self.callbacks = []

    def subscribe(self, callback):
        self.callbacks.append(callback)

    def fire(self, **attrs):
        e = Event()

        e.source = self

        for k, v in attrs.iteritems():
            setattr(e, k, v)

        for fn in self.callbacks:
            print "valores"
            print(e.__dict__)
            fn(e," 5 ")

class CallbackHandler(object):

    valorinicial =  "Hola mundo"
    def __init__(self):
        self.valorinicial = "hola mundo inicializado"

    @staticmethod
    def static_handler(event, valor):
        print  CallbackHandler.valorinicial + " " + valor
        print(event.__dict__)

    def instance_handler(self, event, valor):
        print self.valorinicial + " es " + CallbackHandler.valorinicial + " " + valor
        print(event.__dict__)


# do stuff

o = Observable()
c = CallbackHandler()

# static methods are referenced as <class>.<method>
o.subscribe( CallbackHandler.static_handler )
o.subscribe( c.instance_handler )
o.subscribe( my_callback_func )
o.fire(foo=1,bar=2,copa=3)
