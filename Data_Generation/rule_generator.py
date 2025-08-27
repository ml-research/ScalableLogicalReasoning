"""
RuleGenerator: Generates logical rules for symbolic reasoning tasks.
Supports random rule generation and LLM-guided rule generation.

"""

from language import Language
import random
from transformers import pipeline


class RuleGenerator():
    """
    Generates logical rules for a given language, either randomly or using an LLM-guided approach.
    """

    def __init__(self, language: Language, Rlen: int= 1, Rsample: str= 'random'):
        """
        Initialize the rule generator.
        :param language: The Language object containing vocabulary and grammar.
        :param Rlen: The number of subobject-descriptive predicates to use in the rule.
        :param Rsample: The rule sampling strategy ('random' or 'llm_guided').
        """
        self.language = language
        self.Rlen = Rlen
        self.Rsample = Rsample

    def generate_rule(self) -> str:
        """
        Generate a rule using the selected strategy.
        :return: The generated rule as a string.
        """
        if self.Rsample == 'random':
            return self.generate_random_rule()
        elif self.Rsample == 'llm_guided':
            return self.generate_llm_guided_rule()

    def generate_random_rule(self) -> str:
        """
        Generate a random logical rule using the language's predicates and constants.
        :return: The generated rule as a string.
        """

        language = self.language
        Rlen = self.Rlen

        subobject_variable_numbers = []
        variable_properties = {}
        grounding_text = ''
        while len(subobject_variable_numbers) < Rlen:
            # either add a new subobject variable or use an existing one
            var_num = random.randint(1, max(subobject_variable_numbers) + 1) if len(subobject_variable_numbers) > 0 else 1
            existing_variable = var_num in subobject_variable_numbers
            atom, grounding = sample_atom_and_grounding(language)


            object_identifier = language.vocab.identifiers['object_identifier']
            subobject_identifier = language.vocab.identifiers['subobject_identifier']
            super_to_sub_predicate = language.vocab.identifiers['super_to_sub_predicate']
            subobject_numerating_predicate = language.vocab.identifiers['subobject_numerating_predicate']
            positive_label = language.vocab.identifiers['positive_label']

            var_key = f'{subobject_identifier}{var_num}'

            # if the variable is already used for the same atom, skip it
            if existing_variable:
                if atom in grounding_text:
                    continue 

                # constraints checking:
                subobjects_props = variable_properties[var_key]


                if not language.grammar.validate_grounding(subobjects_props,atom,grounding):
                    continue
 

            # the subobject number must be unique
            if not existing_variable and atom == subobject_numerating_predicate:
                used_subobject_nums = [var_props.get(subobject_numerating_predicate) for var_props in variable_properties.values()]
                if grounding in used_subobject_nums:
                    continue  

            # if we introduce a new subobject variable, add it to the grounding text
            if not existing_variable:
                grounding_text += f'{super_to_sub_predicate}({object_identifier}, {subobject_identifier}{var_num})' if var_num == 1 else f', {super_to_sub_predicate}({object_identifier}, {subobject_identifier}{var_num})'
            subobject_variable_numbers.append(var_num)

            grounding_text += f', {atom}({subobject_identifier}{var_num}, {grounding})'

            # save the properties for each variable to keep the constraints valid 
            if var_key not in variable_properties:
                variable_properties[var_key] = {}
            variable_properties[var_key][atom] = grounding

        return f'{positive_label}({object_identifier}):- {grounding_text}.'


    def generate_llm_guided_rule(self) -> str:
        """
        Generate a logical rule using an LLM, guided by a prompt constructed from the current language.
        :return: The generated rule as a string.
        """
        language = self.language
        Rlen = self.Rlen

        # Build predicate descriptions dynamically
        predicate_lines = []
        for pred, arity in language.vocab.predicates.items():
            args = language.vocab.predicate_arg_types[pred]
            constants = language.vocab.constants[args[1]] if len(args) > 1 and args[1] in language.vocab.constants else []
            constants_str = f" Possible values: {constants}" if constants else ""
            predicate_lines.append(f"- '{pred}({', '.join(args)})':{constants_str}")

        predicate_section = "\n".join(predicate_lines)

        # Build the prompt
        prompt = f"""You are a Prolog rule generator that creates complex and diverse logical rules for a classification task.
        Your task is to generate logically diverse rules, each illustrating a specific logical concept.

        
        Each rule must be in the format:
        {language.vocab.identifiers['positive_label']}({language.vocab.identifiers['object_identifier']}) :- predicate1, predicate2, ..., predicateN.

        You are given a set of predicates that describe objects and their subobjects. The predicates use capitalized variables and lowercase constants.

        Predicates:
        {predicate_section}

        Generate a single Prolog rule that:
        - Uses at most two different subobjects per object.
        - Uses a different logical pattern (see examples below).
        - Uses no more than {Rlen} subobject-descriptive predicates (predicates that describe subobject properties).
        - The predicate {language.vocab.identifiers['super_to_sub_predicate']}({language.vocab.identifiers['object_identifier']}, {language.vocab.identifiers['subobject_identifier']}) is not counted towards this limit.
        - Do not use simple conjunctions.
        - Use only the logical patterns listed below.

        Logical patterns you can use:
        1. Disjunction
        2. Negation
        3. Inequality/Distinctness
        4. Aggregation/Counting
        5. Mutual Exclusion
        6. Uniqueness
        7. No-Other/Uniqueness
        8. Universal Quantification
        9. Conditional Implication
        10. Conditional Aggregation

        Ensure the rule structure is logically consistent and uses only valid Prolog syntax without parentheses.

        Now generate one complex and diverse Prolog rule. The rule must contain no more than {Rlen} subobject-descriptive predicates.
        """

        # Use a HuggingFace pipeline (make sure to install transformers and have access to a suitable model)
        generator = pipeline("text-generation", model="Qwen/Qwen3-4B")  # or another suitable model
        output = generator(prompt, max_new_tokens=1512, do_sample=True, temperature=0.9)[0]['generated_text']
        # Extract the first rule from the output (simple heuristic)
        example_line = f"{self.language.vocab.identifiers['positive_label']}({self.language.vocab.identifiers['object_identifier']}) :- predicate1, predicate2, ..., predicateN."
        for line in output.splitlines():
            line = line.strip()
            if (
                line.startswith(self.language.vocab.identifiers['positive_label'])
                and ":-" in line
                and line != example_line
            ):
                return line
            
        # Fallback: return an empty rule if no rule could be found to run the function again
        return ''
    

def sample_atom_and_grounding(language: Language) -> tuple:
    """
    Randomly sample an atom and its grounding from the language.
    :param language: The language object containing vocabulary and grammar.
    :return: A tuple (atom, grounding).
    """
    # Randomly select a predicate
    atom = random.choice(list(language.vocab.predicates.keys()))

    # Get the argument type for the predicate
    pred_input = language.vocab.predicate_arg_types[atom][1]

    # Retrieve possible groundings for the argument type
    var_groundings = language.vocab.constants[pred_input]

    # Randomly select a grounding
    var_grounding = random.choice(var_groundings)

    return atom, var_grounding