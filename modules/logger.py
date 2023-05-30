class Logger:
    def __init__(self):
        self.colors = {
            'error': '\033[91m',  # rojo
            'info': '\033[94m',  # azul
            'warn': '\033[93m',  # amarillo
            'debug': '\033[95m',  # morado
            'log': '\033[92m',  # verde
        }
        self.reset_color = '\033[0m'  # restablecer color

    def log_action(self, message, level):
        if level not in self.colors:
            print(f"Nivel no válido: {level}")
            return

        color = self.colors[level]
        print(f"{color}[{level.upper()}]{self.reset_color} {message}")

    def error(self, message):
        self.log_action(message, 'error')

    def info(self, message):
        self.log_action(message, 'info')

    def warn(self, message):
        self.log_action(message, 'warn')

    def debug(self, message):
        self.log_action(message, 'debug')

    def log(self, message):
        self.log_action(message, 'log')