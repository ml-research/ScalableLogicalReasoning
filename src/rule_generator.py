# Generic rule extraction function
def extract_rules_from_text(text: str, label: str, object_id: str) -> list:
    '''
    Extract rules of the form label(object_id) :- ... . from the text.
    :param text: The text to extract the rule from
    :param label: The label/predicate name (e.g. 'eastbound')
    :param object_id: The main object (e.g. 'Train')
    :return: List of extracted rules as strings
    '''
    head = f'{label}({object_id}) :-'
    close = '.'
    rules = []
    while head in text:
        start_id = text.find(head)
        end_id = text.find(close, start_id)
        # if there is another head in the text, find the last one
        while text.find(head, start_id + 1, end_id) != -1:
            start_id = text.find(head, start_id + 1, end_id)
        # if no close is found, break
        if end_id == -1:
            break
        rule = text[start_id:end_id + 1]
        rules.append(rule.strip())
        # if the end id is the last character, break
        if end_id + 1 >= len(text):
            break
        text = text[end_id + 1:]
    return rules
# Logical patterns for LLM-guided rule generation, using real label/object/subobject names
def get_logical_patterns(language):
    label = language.vocab.identifiers['positive_label']
    object_id = language.vocab.identifiers['object_identifier']
    subobject_id = language.vocab.identifiers['subobject_identifier']
    super_to_sub = language.vocab.identifiers['super_to_sub_predicate']
    num_pred = language.vocab.identifiers.get('subobject_numerating_predicate', 'num_pred')
    return {
        "Disjunction": f"1. Disjunction: Some {subobject_id} has the property value1 or value2\n{label}({object_id}) :-\n    {super_to_sub}({object_id}, {subobject_id}),\n    (predicate1({subobject_id}, value1) ; predicate2({subobject_id}, value2)).",
        "Negation": f"2. Negation: The {object_id} does not contain any {subobject_id} with property value\n{label}({object_id}) :-\n    \\+ ({super_to_sub}({object_id}, {subobject_id}), predicate({subobject_id}, value)).",
        "Inequality/Distinctness": f"3. Inequality/Distinctness: Two {subobject_id}s must have different property values\n{label}({object_id}) :-\n    {super_to_sub}({object_id}, {subobject_id}A),\n    {super_to_sub}({object_id}, {subobject_id}B),\n    {subobject_id}A \\= {subobject_id}B,\n    predicate({subobject_id}A, value1),\n    predicate({subobject_id}B, value2),\n    value1 \\= value2.",
        "Aggregation/Counting": f"4. Aggregation/Counting: There are more value1 {subobject_id}s than value2 {subobject_id}s\n{label}({object_id}) :-\n    findall({subobject_id}, ({super_to_sub}({object_id}, {subobject_id}), predicate({subobject_id}, value1)), L1),\n    findall({subobject_id}, ({super_to_sub}({object_id}, {subobject_id}), predicate({subobject_id}, value2)), L2),\n    length(L1, N1),\n    length(L2, N2),\n    N1 > N2.",
        "Mutual Exclusion": f"5. Mutual Exclusion: Only one {subobject_id} is value; all others are not value\n{label}({object_id}) :-\n    findall({subobject_id}, ({super_to_sub}({object_id}, {subobject_id}), predicate({subobject_id}, value)), [{subobject_id}X]),\n    forall(( {super_to_sub}({object_id}, {subobject_id}), {subobject_id} \\= {subobject_id}X ), predicate({subobject_id}, NotValue), NotValue \\= value).",
        "Uniqueness": f"6. Uniqueness: No two {subobject_id}s have the same property value\n{label}({object_id}) :-\n    findall(value, ({super_to_sub}({object_id}, {subobject_id}), predicate({subobject_id}, value)), Values),\n    sort(Values, UniqueValues),\n    length(Values, N),\n    length(UniqueValues, N).",
        "No-Other/Uniqueness": f"7. No-Other/Uniqueness: Only two {subobject_id}s in the {object_id}\n{label}({object_id}) :-\n    findall({subobject_id}, {super_to_sub}({object_id}, {subobject_id}), L),\n    length(L, 2).",
        "Universal Quantification": f"8. Universal Quantification: Every property1 {subobject_id} is property2\n{label}({object_id}) :-\n    forall(( {super_to_sub}({object_id}, {subobject_id}), predicate1({subobject_id}, value1) ), predicate2({subobject_id}, value2)).",
        "Conditional Implication": f"9. Conditional Implication: All property1 {subobject_id}s are either value1 or value2\n{label}({object_id}) :-\n    forall(( {super_to_sub}({object_id}, {subobject_id}), predicate1({subobject_id}, value1) ), ( predicate2({subobject_id}, Color), (Color = value1 ; Color = value2) )).",
        "Pattern Matching": f"10. Pattern Matching: All property1 {subobject_id}s are value\n{label}({object_id}) :-\n    forall(( {super_to_sub}({object_id}, {subobject_id}), predicate1({subobject_id}, value1) ), predicate2({subobject_id}, value2)).",
        "Symmetry": f"12. Symmetry: Two {subobject_id}s are neighbors with same property\n{label}({object_id}) :-\n    {super_to_sub}({object_id}, {subobject_id}A),\n    {super_to_sub}({object_id}, {subobject_id}B),\n    {subobject_id}A \\= {subobject_id}B,\n    {num_pred}({subobject_id}A, N1),\n    {num_pred}({subobject_id}B, N2),\n    (N2 =:= N1 + 1 ; N2 =:= N1 - 1),\n    predicate({subobject_id}A, Value),\n    predicate({subobject_id}B, Value).",
        "Combinatorial Group": f"13. Combinatorial Group: Exactly two short yellow {subobject_id}s\n{label}({object_id}) :-\n    findall({subobject_id}, ({super_to_sub}({object_id}, {subobject_id}), predicate1({subobject_id}, value1), predicate2({subobject_id}, value2)), L),\n    length(L, 2).",
        "Recursion": f"14. Recursion: At least one property {subobject_id} in the {object_id}\n{label}([{subobject_id}|{subobject_id}s]) :-\n    predicate({subobject_id}, value)\n    ;\n    {label}({subobject_id}s).",
        "Existence of a Structure": f"15. Existence of a Structure: Exists three {subobject_id}s in sequence: Num, Num+1, Num+2, matching pattern\n{label}({object_id}) :-\n    {super_to_sub}({object_id}, {subobject_id}1), {num_pred}({subobject_id}1, N), predicate1({subobject_id}1, value1),\n    N2 is N+1, N3 is N+2,\n    {super_to_sub}({object_id}, {subobject_id}2), {num_pred}({subobject_id}2, N2), predicate2({subobject_id}2, value2),\n    {super_to_sub}({object_id}, {subobject_id}3), {num_pred}({subobject_id}3, N3), predicate3({subobject_id}3, value3).",
        "Min/Max and Extremal Values": f"16. Min/Max and Extremal Values: A property1 {subobject_id} followed by a property2 {subobject_id} followed by a property3 {subobject_id}, anywhere in the {object_id}\n{label}({object_id}) :-\n    findall(N, ({super_to_sub}({object_id}, {subobject_id}), {num_pred}({subobject_id}, N)), Numbers),\n    max_list(Numbers, Max),\n    {super_to_sub}({object_id}, Last{subobject_id}),\n    {num_pred}(Last{subobject_id}, Max),\n    predicate(Last{subobject_id}, value).",
        "Subset/Superset Constraints": f"17. Subset/Superset Constraints: All property1 {subobject_id}s are among the first three {subobject_id}s.\n{label}({object_id}) :-\n    forall(( {super_to_sub}({object_id}, {subobject_id}), predicate1({subobject_id}, value1) ), ( {num_pred}({subobject_id}, N), N =< 3 )).",
        "Projection/Aggregation Over Multiple Properties": f"18. Projection/Aggregation Over Multiple Properties: All pairs of {subobject_id}s have different (property1, property2) tuples.\n{label}({object_id}) :-\n    {super_to_sub}({object_id}, {subobject_id}A), {super_to_sub}({object_id}, {subobject_id}B), {subobject_id}A \\= {subobject_id}B,\n    predicate1({subobject_id}A, value1A), predicate2({subobject_id}A, value2A),\n    predicate1({subobject_id}B, value1B), predicate2({subobject_id}B, value2B),\n    (value1A \\= value1B ; value2A \\= value2B).",
        "All-Different on Multiple Attributes": f"19. All-Different on Multiple Attributes: Enforce all property1 are different, AND all property2 are different\n{label}({object_id}) :-\n    findall(value1, ({super_to_sub}({object_id}, {subobject_id}), predicate1({subobject_id}, value1)), L1),\n    sort(L1, Unique1),\n    length(L1, N1), length(Unique1, N1),\n    findall(value2, ({super_to_sub}({object_id}, {subobject_id}), predicate2({subobject_id}, value2)), L2),\n    sort(L2, Unique2),\n    length(L2, N2), length(Unique2, N2)."
    }
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
        patterns = get_logical_patterns(language)
        prompt = f"You are a Prolog rule generator that creates complex and diverse logical rules for a classification task.\n"
        prompt += "Your task is to generate logically diverse rules, each illustrating a specific logical concept.\n\n"
        prompt += f"Each rule must be in the format:\n{language.vocab.identifiers['positive_label']}({language.vocab.identifiers['object_identifier']}) :- predicate1, predicate2, ..., predicateN.\n\n"
        prompt += "You are given a set of predicates that describe objects and their subobjects. The predicates use capitalized variables and lowercase constants.\n\n"
        prompt += f"Predicates:\n{predicate_section}\n\n"
        prompt += f"Generate a single Prolog rule that:\n"
        prompt += f"- Uses at most two different subobjects per object.\n"
        prompt += f"- Uses a different logical pattern (see examples below).\n"
        prompt += f"- Uses no more than {Rlen} subobject-descriptive predicates (predicates that describe subobject properties).\n"
        prompt += f"- The predicate {language.vocab.identifiers['super_to_sub_predicate']}({language.vocab.identifiers['object_identifier']}, {language.vocab.identifiers['subobject_identifier']}) is not counted towards this limit.\n"
        prompt += f"- Do not use simple conjunctions.\n"
        prompt += f"- Use only the logical patterns listed below.\n\n"
        prompt += "Logical patterns you can use (replace 'predicate' and 'value' with your language's predicates/constants):\n"
        for name, pattern in patterns.items():
            prompt += f"\n{pattern}\n"
        prompt += "\nEnsure the rule structure is logically consistent and uses only valid Prolog syntax without parentheses.\n\n"
        prompt += f"Now generate one complex and diverse Prolog rule. The rule must contain no more than {Rlen} subobject-descriptive predicates.\n"

        # Use a HuggingFace pipeline (make sure to install transformers and have access to a suitable model)

        generator = pipeline("text-generation", model="Qwen/Qwen3-4B")  # or another suitable model
        output = generator(prompt, max_new_tokens=1512, do_sample=True, temperature=0.9)[0]['generated_text']
        # Use the generic rule extraction function
        label = self.language.vocab.identifiers['positive_label']
        object_id = self.language.vocab.identifiers['object_identifier']
        rules = extract_rules_from_text(output, label, object_id)
        # Filter out rules that are just the example or contain only placeholders
        filtered_rules = []
        for rule in rules:
            # Remove whitespace and check for placeholder patterns
            rule_body = rule.split(':-', 1)[-1].strip().rstrip('.')
            # If the rule body contains only placeholders, skip
            if (
                'predicate' in rule_body or 'predicate2' in rule_body or '...' in rule_body
                or rule_body == ''
            ):
                continue
            filtered_rules.append(rule)
        if filtered_rules:
            return filtered_rules[-1]
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