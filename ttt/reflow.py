"""
Simplify whitespace in text.
Throw in some sentence segmentation for good measure
(not to be taken too seriously)
"""

# author: Eric Kow
# license: Public domain

from .date import read_date


def reflow(tokenizer, text):
    """
    Reflow a TTT text (ignoring the first word if it looks
    like a date)
    """
    words = text.split()
    if words and read_date(words[0]):
        header = [words[0]]
        body = words[1:]
    else:
        header = []
        body = words
    simple = " ".join(body)
    sentences = tokenizer.tokenize(simple)
    return "\n\n".join(header + sentences)
