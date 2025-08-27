from language import Language



class ValidationProgram():
    """
    Represents a validation program consisting of background facts, positive examples, and negative examples.
    """
    
    def __init__(self, background: str, positives: str, negatives: str):
        """
        Initialize the ValidationProgram with background facts, positive examples, and negative examples.
        :param background: The background facts (as string or list of strings)
        :param positives: The positive examples (as string or list of strings)
        :param negatives: The negative examples (as string or list of strings)
        """
        self.background = background  # Background facts for the task
        self.positives = positives    # Positive examples (labels)
        self.negatives = negatives    # Negative examples (labels)

    