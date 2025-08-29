"""
Example usage of the symbolic reasoning framework.
Demonstrates how to use TaskSynthesiser, RuleGenerator, and BackgroundGenerator with different settings.
"""
from language import Grammar, Language, Vocabulary
from task_config import TaskConfig
from task_synthesiser import TaskSynthesiser


# Define a sample language (Train/Car domain)
identifiers = {
    "object_identifier": "Train",
    "subobject_identifier": "Car",
    "super_to_sub_predicate": "has_car",
    "subobject_numerating_predicate": "car_num", # Optional: Set this if you want subobject numbers (e.g. car_num) to be assigned in ascending order and each unique instead of randomly
    "positive_label": "eastbound",
    "negative_label": "westbound"
}
predicates = {
    'has_car': 2,
    'car_num': 2,
    'car_color': 2,
    'car_len': 2,
    'has_wall': 2,
    'has_roof': 2,
    'has_wheel': 2,
    'has_payload': 2,
    'load_num': 2,
    'has_window': 2,
    'car_type': 2,
    'passenger_num': 2,
}
predicate_arg_types = {
    'has_car': ['Train', 'Car'],
    'car_num': ['Car', 'Car_number'],
    'car_color': ['Car', 'Color'],
    'car_len': ['Car', 'Length'],
    'has_wall': ['Car', 'Wall_type'],
    'has_roof': ['Car', 'Roof_type'],
    'has_wheel': ['Car', 'Number_of_wheels'],
    'has_payload': ['Car', 'Load_shape'],
    'load_num': ['Car', 'Number_of_payloads'],
    'has_window': ['Car', 'Window_type'],
    'car_type': ['Car', 'Car_Type'],
    'passenger_num': ['Car', 'Number_of_passengers'],
}
constants = {
    'Train': ['train0', 'train1'],
    'Car': ['car0_1', 'car0_2', 'car1_1', 'car1_2'],
    'Car_number': [1, 2],
    'Color': ['red', 'blue', 'green', 'yellow', 'white'],
    'Length': ['long', 'short'],
    'Wall_type': ['full', 'railing'],
    'Roof_type': ['roof_foundation', 'solid_roof', 'braced_roof', 'peaked_roof', 'none'],
    'Number_of_wheels': [2, 3],
    'Load_shape': ['blue_box', 'golden_vase', 'barrel', 'diamond', 'metal_pot', 'oval_vase', 'none'],
    'Number_of_payloads': [0, 1, 2, 3],
    'Window_type': ['full', 'half', 'none'],
    'Car_Type': ['passenger', 'freight', 'mixed'],
    'Number_of_passengers': list(range(0, 11)),
}


# This function should implement all logical constraints for valid predicate groundings.
# Here we restrict which values are allowed given certain conditions, e.g. only has_wheel=2 for short cars
def validate_grounding(map_predicate_value: dict, predicate: str, value: str) -> bool:

        if map_predicate_value.get('car_len') == 'short':
            if predicate == 'has_wheel' and value != 2:
                return False

            if predicate == 'load_num' and value > 2:
                return False

        if map_predicate_value.get('load_num') == 0:
            if predicate == 'has_payload' and value != 'none':
                return False

        if map_predicate_value.get('load_num') != 0:
            if predicate == 'has_payload' and value == 'none':
                return False

            if predicate == 'car_type' and value == 'passenger':
                return False

        if map_predicate_value.get('has_payload') == 'none':
            if predicate == 'load_num' and value != 0:
                return False

        if map_predicate_value.get('has_payload') != 'none':
            if predicate == 'car_type' and value == 'passenger':
                return False
            if predicate == 'load_num' and value == 0:
                return False

        if map_predicate_value.get('car_type') == 'passenger':
            if predicate == 'has_payload' and value != 'none':
                return False
            if predicate == 'load_num' and value != 0:
                return False

        if map_predicate_value.get('car_type') == 'freight':
            if predicate == 'passenger_num' and value != 0:
                return False

        if map_predicate_value.get('has_wheel') == 3:
            if predicate == 'car_len' and value == 'short':
                return False

        if map_predicate_value.get('passenger_num') != 0:
            if predicate == 'car_type' and value == 'freight':
                return False
            
        return True

grammar = Grammar(_validate_grounding_func=validate_grounding)
vocab = Vocabulary(identifiers=identifiers, predicates=predicates, predicate_arg_types=predicate_arg_types, constants=constants)
language = Language(vocab=vocab, grammar=grammar)

# Example 1: Random rule, uniform background
task_config_uniform = TaskConfig(Rlen=2, Rsample='random', B_pi='uniform', kappa=(1,1))
synthesiser_uniform = TaskSynthesiser()
rule, program, prompt = synthesiser_uniform.generate_task(language=language, task_config=task_config_uniform)
print("--- Example 1: Random rule, uniform background ---")
print("Rule:", rule)
print("Prompt:\n", prompt)

# Example 2: LLM-guided rule, mirror background
task_config_mirror = TaskConfig(Rlen=2, Rsample='llm_guided', B_pi='mirror', kappa=(1,1))
synthesiser_mirror = TaskSynthesiser()
rule, program, prompt = synthesiser_mirror.generate_task(language=language, task_config=task_config_mirror)
print("\n--- Example 2: LLM-guided rule, mirror background ---")
print("Rule:", rule)
print("Prompt:\n", prompt)

# Example 3: Random rule, custom background with probability distribution, for predicates without probability distribution random distribution will be used
B_pi = {
    'car_color': {'red': 0.7, 'blue': 0.1, 'green': 0.1, 'yellow': 0.05, 'white': 0.05},
    'car_type': {'passenger': 0.5, 'freight': 0.3, 'mixed': 0.2}
}
task_config_custom = TaskConfig(Rlen=2, Rsample='random', B_pi=B_pi, kappa=(1,1))
synthesiser_custom = TaskSynthesiser()
rule, program, prompt = synthesiser_custom.generate_task(language=language, task_config=task_config_custom)
print("\n--- Example 3: Random rule, custom background (probabilities) ---")
print("Rule:", rule)
print("Prompt:\n", prompt)
