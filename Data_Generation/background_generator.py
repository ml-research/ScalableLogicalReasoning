"""
BackgroundGenerator: Generates logical backgrounds (facts) for objects and subobjects in a symbolic reasoning task.
Supports uniform, mirror, and custom background generation strategies.

"""

from evaluate import load
from language import Language
from typing import Union, Dict
import random
import re
from utils import assign_label, extract_object_name, extract_predicate_value

class BackgroundGenerator():
    """
    Generates background facts for logical reasoning tasks using different strategies (uniform, mirror, custom).
    """

    def __init__(self, language: Language, B_pi: Union[str, Dict[str, float]]):
        """
        Initialize the background generator.
        :param language: The Language object containing vocabulary and grammar.
        :param B_pi: The background generation strategy ('uniform', 'mirror', or a custom dict).
        """
        self.language = language
        self.B_pi = B_pi

    def generate_background(self, rule: str, sample_index: int, first_sample: str=None) -> str:
        """
        Generate a background using the selected strategy.
        :param rule: The rule for which the background is generated.
        :param sample_index: The index of the sample to generate.
        :param first_sample: (Optional) The first sample for mirror background generation.
        :return: The generated background as a string.
        """
        if isinstance(self.B_pi, str):
            if self.B_pi == 'uniform':
                return self.generate_uniform_background(language=self.language, sample_index=sample_index)
            elif self.B_pi == 'mirror':
                return self.generate_mirror_background(language=self.language, first_sample=first_sample, rule=rule, sample_index=sample_index)
            else:
                raise ValueError("B_pi must be 'uniform' or 'mirror'")
        elif isinstance(self.B_pi, dict):
            return self.generate_custom_background(language=self.language, sample_index=sample_index)
        else:
            raise TypeError("B_pi must be a string or a dictionary")


    def generate_uniform_background(self, language: Language, sample_index: int):
        """
        Generate a uniform background: all objects and subobjects are distributed evenly.
        :param language: The Language object.
        :param sample_index: The index of the sample to generate.
        :return: The generated background as a string.
        """
        complete_sample = ''
        m_subobjects = f''
        

        object_identifier = language.vocab.identifiers['object_identifier']
        subobject_identifier = language.vocab.identifiers['subobject_identifier']

        if subobject_identifier not in language.vocab.constants:
            raise ValueError(f"Language vocabulary must contain Subobject :{subobject_identifier} constant for uniform background generation")


        if object_identifier not in language.vocab.constants:
            raise ValueError(f"Language vocabulary must contain Object: {object_identifier} constant for uniform background generation")
        else:
            sample_name = language.vocab.constants[object_identifier][sample_index]

        super_to_sub_predicate = language.vocab.identifiers['super_to_sub_predicate']
        subobject_numerating_predicate = language.vocab.identifiers['subobject_numerating_predicate']

        if len(language.vocab.constants[subobject_identifier]) % len(language.vocab.constants[object_identifier]) != 0:
            raise ValueError("Number of subobjects must be divisible by number of objects for uniform background generation")

        num_subobjects = len(language.vocab.constants[subobject_identifier]) // len(language.vocab.constants[object_identifier])

        predicates = language.vocab.predicates.keys()
        constants = language.vocab.constants

        complete_sample += sample_name + '\n'
        for j in range(num_subobjects):
            constants = language.vocab.constants.copy()  # Copy constants to avoid modifying the original

            predicates_value_map = {}

            m_sample_subobject = ''
            subobject_name = 'Empty_Subobject_Name'
            for predicate in predicates:
                pred_input = language.vocab.predicate_arg_types[predicate][1]

                # Retrieve possible groundings for the argument type
                var_groundings = constants[pred_input]
 

                var_grounding = (random.choice(var_groundings))

                predicate_sampling_count = 0
                while not language.grammar.validate_grounding(predicates_value_map, predicate, var_grounding) and predicate != super_to_sub_predicate and predicate != subobject_numerating_predicate:
                    if predicate_sampling_count > 1000:
                        return ''
                    var_grounding = random.choice(var_groundings)
                    predicate_sampling_count += 1


                if predicate == super_to_sub_predicate:
                    var_grounding = var_groundings[j+sample_index*num_subobjects]
                    subobject_name = var_grounding
                    m_sample_subobject += f'{predicate}({sample_name}, {var_grounding}).\n'
                else:
                    if predicate == subobject_numerating_predicate:
                        var_grounding = var_groundings[j]
                    m_sample_subobject += f'{predicate}({subobject_name}, {var_grounding}).\n'
                
                predicates_value_map[predicate] = var_grounding

            
            m_subobjects += f'{m_sample_subobject}'
        complete_sample += f'{m_subobjects}\n'

        return complete_sample

    def generate_mirror_background(self, language: Language, first_sample: str, rule: str, sample_index: int) -> str:
        """
        Generate a mirror background: mirrors the structure of a given first sample, but with new objects/subobjects.
        :param language: The Language object.
        :param first_sample: The sample to mirror (as a string).
        :param rule: The rule for which the background is generated.
        :param sample_index: The index of the sample to generate.
        :return: The generated background as a string.
        """


        if first_sample == None or first_sample == '':

            symbolic_judge = load("AIML-TUDA/VerifiableRewardsForScalableLogicalReasoning")
            
            positive_sample =  self.generate_uniform_background(language=language, sample_index=sample_index)
            y, q = assign_label(language=language, rule=rule, background=positive_sample, symbolic_judge=symbolic_judge)
            # the generated first sample have a positive label
            count = 0
            while y != 1:
                if count > 10:
                    return ''
                positive_sample =  self.generate_uniform_background(language=language, sample_index=sample_index)
                y, q = assign_label(language=language, rule=rule, background=positive_sample, symbolic_judge=symbolic_judge)
                count += 1
            return positive_sample

        object_identifier = language.vocab.identifiers['object_identifier']
        subobject_identifier = language.vocab.identifiers['subobject_identifier']
        super_to_sub_predicate = language.vocab.identifiers['super_to_sub_predicate']
        subobject_numerating_predicate = language.vocab.identifiers['subobject_numerating_predicate']

        if subobject_identifier not in language.vocab.constants:
            raise ValueError(f"Language vocabulary must contain Subobject :{subobject_identifier} constant for uniform background generation")


        if object_identifier not in language.vocab.constants:
            raise ValueError(f"Language vocabulary must contain Object: {object_identifier} constant for uniform background generation")
        else:
            sample_name = language.vocab.constants[object_identifier][sample_index]


        if len(language.vocab.constants[subobject_identifier]) % len(language.vocab.constants[object_identifier]) != 0:
            raise ValueError("Number of subobjects must be divisible by number of objects for uniform background generation")

        num_subobjects = len(language.vocab.constants[subobject_identifier]) // len(language.vocab.constants[object_identifier])



        old_object = extract_object_name(first_sample, super_to_sub_predicate)

        first_sample = first_sample.replace(old_object, sample_name)

        #split the subobjects by super_to_sub_predicate
        #super_to_sub_predicate must still be in the part the example sample would therefore be split in three parts

        split_by_subobjects = re.split(rf'(?={super_to_sub_predicate})', first_sample)
        subobjects = split_by_subobjects[1:]

        for i,subobject in enumerate(subobjects):
            constants = language.vocab.constants

            old_subobject_name = extract_predicate_value(subobject, super_to_sub_predicate)
            subobject = subobject.replace(old_subobject_name, constants[subobject_identifier][i+sample_index*num_subobjects])
            lines = subobject.strip().split('\n')
            predicates_value_map = {}
            for line in lines:
                match = re.match(r'^([^(]+)\(', line)
                if match:
                    subobject_predicate = match.group(1).strip()
                    predicates_value_map[subobject_predicate] = extract_predicate_value(line, subobject_predicate)

            corrected_lines = []
            for line in lines:
                match = re.match(r'^([^(]+)\(', line)
                if match:
                    subobject_predicate = match.group(1).strip()
                    value_in_sample = extract_predicate_value(line, subobject_predicate)
                    value_in_rule = extract_predicate_value(rule, subobject_predicate)
                    if subobject_predicate in rule and subobject_predicate != super_to_sub_predicate and value_in_sample == value_in_rule and subobject_predicate != subobject_numerating_predicate:
                        pred_input = language.vocab.predicate_arg_types[subobject_predicate][1]
                        # Retrieve possible groundings for the argument type
                        var_groundings = constants[pred_input]
                        var_grounding = random.choice(var_groundings)
                        predicate_sampling_count = 0
                        while not language.grammar.validate_grounding(predicates_value_map, subobject_predicate, var_grounding) or var_grounding == value_in_rule:
                            var_grounding = random.choice(var_groundings)
                            predicate_sampling_count += 1
                            if predicate_sampling_count > 1000:
                                return ''
                        predicates_value_map[subobject_predicate] = var_grounding
                        line = line.replace(value_in_sample, str(var_grounding))
                corrected_lines.append(line.strip())

            # Replace the original subobject definition with the corrected one
            subobjects[i] = '\n'.join(corrected_lines)

        sample = ''
        sample += f'{sample_name}.\n'
        for subobject in subobjects:
            sample += f'{subobject}\n'

        return sample

    def generate_custom_background(self, language: Language, sample_index: int):
        """
        Generate a custom background: all predicates are grounded, but the value for each predicate is sampled according to a probability distribution specified in self.B_pi.
        :param language: The Language object.
        :param sample_index: The index of the sample to generate.
        :return: The generated background as a string.
        """
        complete_sample = ''
        m_subobjects = ''

        object_identifier = language.vocab.identifiers['object_identifier']
        subobject_identifier = language.vocab.identifiers['subobject_identifier']

        if subobject_identifier not in language.vocab.constants:
            raise ValueError(f"Language vocabulary must contain Subobject :{subobject_identifier} constant for custom background generation")
        if object_identifier not in language.vocab.constants:
            raise ValueError(f"Language vocabulary must contain Object: {object_identifier} constant for custom background generation")
        else:
            sample_name = language.vocab.constants[object_identifier][sample_index]

        super_to_sub_predicate = language.vocab.identifiers['super_to_sub_predicate']
        subobject_numerating_predicate = language.vocab.identifiers['subobject_numerating_predicate']

        if len(language.vocab.constants[subobject_identifier]) % len(language.vocab.constants[object_identifier]) != 0:
            raise ValueError("Number of subobjects must be divisible by number of objects for custom background generation")

        num_subobjects = len(language.vocab.constants[subobject_identifier]) // len(language.vocab.constants[object_identifier])
        predicates = language.vocab.predicates.keys()
        constants = language.vocab.constants

        complete_sample += sample_name + '\n'
        for j in range(num_subobjects):
            constants = language.vocab.constants.copy()
            predicates_value_map = {}
            m_sample_subobject = ''
            subobject_name = 'Empty_Subobject_Name'
            for predicate in predicates:
                pred_input = language.vocab.predicate_arg_types[predicate][1]
                var_groundings = constants[pred_input]
                # Use probability distribution from self.B_pi for this predicate/value
                if predicate in self.B_pi:
                    value_probs = self.B_pi[predicate]
                    # value_probs is a dict: value -> probability
                    values, probs = zip(*[(v, value_probs.get(v, 0.0)) for v in var_groundings])
                    # Normalize probabilities in case they don't sum to 1
                    total = sum(probs)
                    if total == 0:
                        # fallback: uniform
                        probs = [1/len(values)]*len(values)
                    else:
                        probs = [p/total for p in probs]
                    var_grounding = random.choices(values, weights=probs, k=1)[0]
                else:
                    # fallback: uniform
                    var_grounding = random.choice(var_groundings)

                predicate_sampling_count = 0
                while not language.grammar.validate_grounding(predicates_value_map, predicate, var_grounding) and predicate != super_to_sub_predicate and predicate != subobject_numerating_predicate:
                    if predicate_sampling_count > 1000:
                        return ''
                    if predicate in self.B_pi:
                        value_probs = self.B_pi[predicate]
                        values, probs = zip(*[(v, value_probs.get(v, 0.0)) for v in var_groundings])
                        total = sum(probs)
                        if total == 0:
                            probs = [1/len(values)]*len(values)
                        else:
                            probs = [p/total for p in probs]
                        var_grounding = random.choices(values, weights=probs, k=1)[0]
                    else:
                        var_grounding = random.choice(var_groundings)
                    predicate_sampling_count += 1

                if predicate == super_to_sub_predicate:
                    var_grounding = var_groundings[j+sample_index*num_subobjects]
                    subobject_name = var_grounding
                    m_sample_subobject += f'{predicate}({sample_name}, {var_grounding}).\n'
                else:
                    if predicate == subobject_numerating_predicate:
                        var_grounding = var_groundings[j]
                    m_sample_subobject += f'{predicate}({subobject_name}, {var_grounding}).\n'
                predicates_value_map[predicate] = var_grounding
            m_subobjects += f'{m_sample_subobject}'
        complete_sample += f'{m_subobjects}\n'
        return complete_sample


