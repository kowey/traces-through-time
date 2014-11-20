"""
Simplify whitespace in text.
Throw in some sentence segmentation for good measure
(not to be taken too seriously)
"""

# author: Eric Kow
# license: Public domain

def reflow(tokenizer, text):
    simple = " ".join(text.split())
    sentences = tokenizer.tokenize(simple)
    return "\n\n".join(sentences)
