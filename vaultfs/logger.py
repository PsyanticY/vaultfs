import logging

# Is there a simpler way to put the Formatter class inside of the vaultfslogger class directly ?

class Formatter(logging.Formatter):

    def __init__(self):
        super().__init__(fmt="%(name)s::%(asctime)s::%(levelname)s - %(message)s", style='%')

    def format(self, record):

        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._style._fmt

        # Replace the original format with one customized by logging level
        if record.levelno == logging.WARNING:
            self._style._fmt = "%(name)s::%(asctime)s::WARNING - %(message)s"

        elif record.levelno == logging.INFO:
            self._style._fmt = "%(name)s::%(asctime)s::INFO - %(message)s"

        elif record.levelno == logging.ERROR:
            self._style._fmt = "%(name)s::%(asctime)s::ERROR - %(message)s"

        result = logging.Formatter.format(self, record)
        self._style._fmt = format_orig
        return result

class VaultfsLogger(object):

    def __init__(self, name='VaultFS', level=logging.INFO):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            self.logger = logging.getLogger(name)
            self.logger.setLevel(level)

            console_handler = logging.StreamHandler()
            # formatter
            my_formatter = Formatter()
            console_handler.setFormatter(my_formatter)
            self.logger.addHandler(console_handler)
        else:
            return None

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)