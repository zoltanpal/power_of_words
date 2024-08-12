import re

from jinja2.filters import FILTERS


def highlight_words(text, word_list):
    for word in word_list:
        regex = re.compile(f"{re.escape(word)}", re.IGNORECASE)
        text = regex.sub(
            lambda match: f'<mark class="highlight">{match.group()}</mark>', text
        )
    return text


def initialize_filters():
    # Add the custom function to the environment
    FILTERS["highlight_words"] = highlight_words
