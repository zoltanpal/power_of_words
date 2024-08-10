import logging
import re


def setup_logging_to_file(log_file, log_level=logging.DEBUG) -> logging.Logger:
    """
    Sets up logging to a specified file with a given log level.

    Args:
        log_file (str): The path to the log file.
        log_level (int): The logging level (default is logging.DEBUG).

    Returns:
        logging.Logger: A configured logger object.
    """


    # Create a logger specific to the log file
    logger = logging.getLogger(log_file)
    logger.setLevel(log_level)  # Set the log level for the logger

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

    # Create a file handler for the log file
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)  # Set the log level for the file handler
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    return logger


def clean_url(url: str) -> str:
    """
    Cleans a URL by removing specific patterns like "/rss" or "/feed".

    Args:
        url (str): The URL to be cleaned.

    Returns:
        str: The cleaned URL.
    """
    # Define regex pattern to match "/rss" or "/feed"
    pattern = r'/rss|/feed'
    return re.sub(pattern, '', url)


def remove_photo_video(text: str) -> str:
    """
    Removes references to photos or videos from a text.

    Args:
        text (str): The text to be cleaned.

    Returns:
        str: The text with photo and video references removed.
    """

    pattern = re.compile(r'\s*[-+]\s*(fotó(?:kkal)?|videó(?:kkal)?|fotók|videók)?[!.,;]?\s*$|\s+fotó\s*$',
                         re.IGNORECASE)
    return re.sub(pattern, '', text)


def jsonify_query_result(query_result) -> List[dict]:
    """
    Converts an SQLAlchemy query result to a list of dictionaries for JSON serialization.

    Args:
        query_result: The SQLAlchemy query result.

    Returns:
        List[dict]: A list of dictionaries representing the query result.
    """
    result_dict_list = []
    for row in query_result:
        row_dict = {key: value for key, value in row.__dict__.items() if not key.startswith('_sa_')}
        result_dict_list.append(row_dict)
    return result_dict_list
