"""
Example usage of the symbolic reasoning framework.
Demonstrates how to use TaskSynthesiser, RuleGenerator, and BackgroundGenerator with different settings.
"""
from language import Grammar, Language, Vocabulary
from task_config import TaskConfig
from task_synthesiser import TaskSynthesiser


# Define a sample language (House/Room domain)
identifiers = {
    "object_identifier": "House",
    "subobject_identifier": "Room",
    "super_to_sub_predicate": "has_room",
    "subobject_numerating_predicate": "room_num",
    "positive_label": "northbound",
    "negative_label": "southbound"
}
predicates = {
    'has_room': 2,
    'room_num': 2,
    'has_wall_color': 2,
    'has_roof_type': 2,
    'has_garden': 2,
    'has_garage': 2,
    'has_window': 2
}
predicate_arg_types = {
    'has_room': ['House', 'Room'],
    'room_num': ['Room', 'Room_number'],
    'has_wall_color': ['Room', 'Color'],
    'has_roof_type': ['Room', 'Roof_type'],
    'has_garden': ['Room', 'Garden_type'],
    'has_garage': ['Room', 'Garage_type'],
    'has_window': ['Room', 'Window_type'],
}
constants = {
    'House': ['house0', 'house1', 'house2', 'house3'],
    'Room': ['room0_1', 'room0_2', 'room1_1', 'room1_2','room2_1', 'room2_2', 'room3_1', 'room3_2'],
    'Room_number': [1, 2],
    'Color': ['red', 'blue', 'green', 'yellow', 'white'],
    'Roof_type': ['flat', 'gabled', 'hipped', 'none'],
    'Garden_type': ['flower', 'vegetable', 'herb', 'none'],
    'Garage_type': ['attached', 'detached', 'none'],
    'Window_type': ['bay', 'casement', 'sliding', 'none'],
}


# This function should implement all logical constraints for valid predicate groundings.
# Here we restrict which values are allowed given certain conditions
def validate_grounding(map_predicate_value: dict, predicate: str, value: str) -> bool:

        if map_predicate_value.get('has_roof_type') == 'flat':
            if predicate == 'has_window' and value != 'bay':
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
    'has_wall_color': {'red': 0.7, 'blue': 0.1, 'green': 0.1, 'yellow': 0.05, 'white': 0.05},
    'has_roof_type': {'flat': 0.5, 'gabled': 0.3, 'hipped': 0.2,'none': 0.0}
}
task_config_custom = TaskConfig(Rlen=2, Rsample='random', B_pi=B_pi, kappa=(1,1))
synthesiser_custom = TaskSynthesiser()
rule, program, prompt = synthesiser_custom.generate_task(language=language, task_config=task_config_custom)
print("\n--- Example 3: Random rule, custom background (probabilities) ---")
print("Rule:", rule)
print("Prompt:\n", prompt)
