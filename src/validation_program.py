from language import Language



class ValidationProgram():
    """
    Represents a validation program consisting of background facts, positive examples, and negative examples.
    """

    def __init__(self, background: str, positives: str, negatives: str, language: Language):
        """
        Initialize the ValidationProgram with background facts, positive examples, and negative examples.
        :param background: The background facts (as string or list of strings)
        :param positives: The positive examples (as string or list of strings)
        :param negatives: The negative examples (as string or list of strings)
        :param language: The language used for the validation program
        """
        self.background = background  # Background facts for the task
        self.positives = positives    # Positive examples (labels)
        self.negatives = negatives    # Negative examples (labels)
        self.language = language      # Language used for the validation program

    def get_validation_program(self) -> str:
        """
        Returns the full validation program as a single string.
        :return: The validation program combining background, positives, and negatives.
        """
        def extract_object_from_facts(facts, object_identifier):
            # Extracts the object name from the first matching predicate line in the facts.
            for line in facts.splitlines():
                if object_identifier in line:
                    start = line.find('(') + 1
                    end = line.find(',', start)
                    if start > 0 and end > start:
                        return line[start:end].strip()
            return None
        
        Validation_program = ""
        examples = []
        for facts in self.background :
            obj = extract_object_from_facts(facts, self.language.vocab.identifiers['super_to_sub_predicate'])
            # Find the matching label for this object
            label = next((l for l in self.positives + self.negatives if obj and obj in l), None)
            if label:
                examples.append(label + "\n" + facts)
        Validation_program += "\n\n".join(examples)
        return Validation_program

    