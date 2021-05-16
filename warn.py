"""
File: warnings.py
-----------------

Helper classes to generate warnings for the posting.
"""
from utils import Posting
from typing import Callable, Union, Iterable

class WarningDiscriminator:
    def __init__(
        self,
        eval_fn: Callable[[Posting], Union[str, None]] = lambda p: None
    ):
        """
        Arguments
        ---------
        eval_fn -- The function used for evaluating whether the posting should
            receive a warning. Either returns the warning (as a string) or
            None if there's no warning needed.
        """
        self.eval_fn = eval_fn


    def evaluate(self, p: Posting) -> Union[str, None]:
        """
        Evaluates the warning on the posting and returns the result.
        """
        return self.eval_fn(p)


    @classmethod
    def price_too_low(cls, min_price: int):
        """
        Creates a warning if the price falls below min_price.
        """
        def eval_fn(p: Posting):
            if p.price < min_price:
                return f"The price (${p.price}) is suspiciously low."

        return cls(eval_fn)


    @classmethod
    def no_image(cls):
        """
        Creates a warning if there's no image.
        """
        def eval_fn(p: Posting):
            if p.img_url is None:
                return f"I couldn't find any images for this posting."

        return cls(eval_fn)


    @classmethod
    def unfurnished(cls):
        """
        Creates a warning if the posting is unfurnished.
        """
        def eval_fn(p: Posting):
            if 'furnished' not in p.attrs:
                return "The posting appears to be unfurnished."

        return cls(eval_fn)


    @classmethod
    def shared_space(cls):
        """
        Creates a warning if any of the attributes have "no private" in them.
        """
        def eval_fn(p: Posting):
            if any(a.startswith('no private') for a in p.attrs):
                return f"The posting appears to have shared spaces."

        return cls(eval_fn)


class WarningPipeline:
    def __init__(self, *pipeline: Iterable[WarningDiscriminator]):
        """
        Arguments
        ---------
        pipeline -- A collection of tests that need to be run on the posting.
        """
        if not pipeline:
            pipeline = []

        self.pipeline = list(pipeline)


    def run_on(self, p: Posting) -> Posting:
        """
        Applies each of the warnings to the posting. Returns the posting after
        it's been modified
        """
        p.warnings = []

        for warning in self.pipeline:
            w = warning.evaluate(p)
            if w:
                p.warnings.append(w)

        return p
