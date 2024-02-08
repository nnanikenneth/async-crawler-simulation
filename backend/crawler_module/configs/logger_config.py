import logging
import logging.handlers
import os

class LoggerConfig:
    """
    Configuration class for setting up logging in a web crawler application.

    This class defines the logging format, base directory for log files, specifies log files for different logging levels,
    and provides a static method to set up logging handlers for each level. It ensures that log messages are appropriately
    categorized and saved into separate files based on their severity levels.

    Attributes:
        LOG_FORMAT (str): The format string for log messages, including the timestamp, log level, thread name, logger name, and the log message itself.
        BASE_DIR (str): The absolute path to the directory where log files will be stored. It is dynamically set to a 'logs' directory relative to the script location.
        LOG_FILES (dict): A dictionary mapping logging levels to their respective log file names.

    Methods:
        setup_logging(): Sets up file handlers for each logging level specified in `LOG_FILES`, configuring them to write to separate files.
    """

    LOG_FORMAT = "%(asctime)s [%(levelname)s] %(threadName)s %(name)s: %(message)s"
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))

    LOG_FILES = {
        "DEBUG": "web_crawler_debug.log",
        "INFO": "web_crawler_info.log",
        "WARNING": "web_crawler_warning.log",
        "ERROR": "web_crawler_error.log",
        "CRITICAL": "web_crawler_critical.log",
    }

    @staticmethod
    def setup_logging():
        """
        Sets up logging for the application.

        This method checks if the log directory exists, creates it if necessary, and then sets up a file handler for each
        log level defined in `LOG_FILES`. Each handler formats messages according to `LOG_FORMAT` and writes them to the
        corresponding file. It is designed to capture logs across all levels, ensuring detailed logging information is
        available for debugging and monitoring the application.

        No parameters.

        Returns:
            None. However, it outputs logging setup completion info to the INFO log.

        Side Effects:
            - Creates log files in the specified `BASE_DIR` directory.
            - Adds multiple file handlers to the root logger.
        """
        if not os.path.exists(LoggerConfig.BASE_DIR):
            os.makedirs(LoggerConfig.BASE_DIR)

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        for level, log_file in LoggerConfig.LOG_FILES.items():
            file_handler = logging.FileHandler(
                os.path.join(LoggerConfig.BASE_DIR, log_file)
            )
            # Think about retention policy or using a rotating file handler...however,
            # don't think too much about since this is not the primary focus of the project
            # file_handler = logging.handlers.RotatingFileHandler(os.path.join(LoggerConfig.BASE_DIR, log_file), maxBytes=5*1024*1024, backupCount=5)
            file_handler.setLevel(getattr(logging, level))
            file_formatter = logging.Formatter(LoggerConfig.LOG_FORMAT)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        logging.info("Logging setup complete.")


# Example usage
"""
def main():
    # Setup logging as per the LoggerConfig class.
    LoggerConfig.setup_logging()

    # You can start logging messages.
    logging.debug("This is a debug message.")
    logging.info("This is an info message.")
    logging.warning("This is a warning message.")
    logging.error("This is an error message.")
    logging.critical("This is a critical message.")

if __name__ == "__main__":
    main()
"""
