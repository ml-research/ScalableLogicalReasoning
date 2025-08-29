"""
PromptGenerator: Generates a natural language prompt for logical reasoning tasks.
The prompt describes the logical problem, available predicates, and provides labeled examples.
It is fully generic and adapts to any domain described by the Language object.
"""

from language import Language

class PromptGenerator():
    """
    Generates a prompt for a logical reasoning task, including predicate descriptions and labeled examples.
    """

    @staticmethod
    def generate_prompt(background: list, positives: list, negatives: list, language: Language) -> str:
        """
        Generate a prompt for a logical reasoning task.
        :param background: List of background fact strings (one per example, without label).
        :param positives: List of positive label strings (e.g., eastbound(train1).).
        :param negatives: List of negative label strings (e.g., westbound(train2).).
        :param language: The Language object describing the domain.
        :return: The generated prompt as a string.
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


        super_to_sub_predicate = language.vocab.identifiers["super_to_sub_predicate"]

        prompt = ""
        # Compose the opening section using the identifiers from the language
        object_identifier = language.vocab.identifiers["object_identifier"]
        subobject_identifier = language.vocab.identifiers["subobject_identifier"]
        positive_label = language.vocab.identifiers["positive_label"]
        negative_label = language.vocab.identifiers["negative_label"]

        opening = f"""You are a classifier for a logical reasoning task. Each {object_identifier} is composed of one or more {subobject_identifier}s, and each {subobject_identifier} is characterized by a set of properties, represented as ground atoms over a fixed set of predicates.\nThe label ({positive_label} or {negative_label}) of a {object_identifier} is to be determined from its composition.\n\nTo describe the {object_identifier}s we define a set of predicates and grounding domains:"""
        prompt += opening + "\n"

        vocab = language.vocab

        # List all predicates and their possible values
        for word in vocab.predicate_arg_types:
            values = [f'{v}' for v in vocab.constants[vocab.predicate_arg_types[word][1]]]
            values = ', '.join(values)
            prompt += f"- '{word}({vocab.predicate_arg_types[word][0]}, {vocab.predicate_arg_types[word][1]})': {vocab.predicate_arg_types[word][1]} can be {values}.\n"

        # Add the example list opening, describing the format of examples
        example_list_opening = f"""You are provided with positive and negative examples in the form of {positive_label}(t) or {negative_label}(t) for each {object_identifier} t, together with background knowledge consisting of ground facts over the above predicates which describe its composition."""
        prompt += "\n"+ example_list_opening + "\n\n"

        # Add all examples, preserving the order of background
        examples = []
        for facts in background:
            obj = extract_object_from_facts(facts, super_to_sub_predicate)
            # Find the matching label for this object
            label = next((l for l in positives + negatives if obj and obj in l), None)
            if label:
                examples.append(label + "\n" + facts)
        prompt += "\n\n".join(examples) + "\n\n"

        # Add the closing instructions
        closing = f"""Your task is to formulate a hypothesis in form of a prolog rule of the form '{positive_label}(T) :- Body.' that correctly distinguishes {positive_label} from {negative_label} {object_identifier}s. The hypothesis must be true for all positive examples (i.e., {object_identifier}s labeled as {positive_label}) and false for all negative examples (i.e., {object_identifier}s labeled as {negative_label}). Aim to find the shortest correct rule, that is, one that uses the fewest possible body literals without loss of conditions. Your rule must use only the predicates defined in the grammar above and must perfectly separate {positive_label} from {negative_label} {object_identifier}s."""
        prompt += closing

        return prompt


