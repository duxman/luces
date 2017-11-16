import config
from logger import clienteLog

def main():
    Logger.info("--------------------<<  INI  >>--------------------")
    Logger.info("Arrancamos la ejecucion")
    Config = config.GeneralConfiguration( Logger )
    # my code here


if __name__ == "__main__":
    cliente = clienteLog()
    Logger = cliente.InicializaLog()
    main()