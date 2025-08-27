from dataclasses import dataclass, field
from typing import Dict, List, Any,Callable

MANDATORY_IDENTIFIERS = [
    "object_identifier",         # e.g. "Train"
    "subobject_identifier",      # e.g. "Car"
    "super_to_sub_predicate",    # e.g. "has_car"
    "subobject_numerating_predicate", # e.g. "car_num"
    "positive_label", # e.g. "eastbound"
    "negative_label"  # e.g. "westbound"
]


@dataclass
class Vocabulary:
    """
    Holds predicate signatures and constant domains.
    - identifiers: mandatory specifications for the identifiers of the logical problem
    - predicates: mapping predicate_name -> arity
    - predicate_arg_types: mapping predicate_name -> list of type keys (same length as arity)
    - constants: mapping type_key -> list of constant values
    """
    identifiers: Dict[str, str]
    predicates: Dict[str, int]
    predicate_arg_types: Dict[str, List[str]]
    constants: Dict[str, List[Any]] = field(default_factory=dict)

    def __post_init__(self):
        missing = [k for k in MANDATORY_IDENTIFIERS if k not in self.identifiers]
        if missing:
            raise ValueError(f"Missing mandatory identifiers: {missing}")


@dataclass
class Grammar:
    """
    Encapsulates the logical constraints (grammar) for valid predicate groundings.
    The grammar is defined by a custom validation function, which checks if a predicate grounding is allowed
    given the current assignments (map_predicate_value) and the value to be assigned.
    """
    _validate_grounding_func: Callable[[dict, str, str], bool] = None  # Custom validation function

    def validate_grounding(self, map_predicate_value: dict, predicate: str, value: str) -> bool:
        """
        Checks if a predicate grounding is valid according to the grammar's validation function.
        :param map_predicate_value: Dictionary of already assigned predicate values for the current subobject.
        :param predicate: The predicate to check.
        :param value: The value to assign to the predicate.
        :return: True if the grounding is valid, False otherwise.
        """
        if self._validate_grounding_func:
            # Use the custom validation function if provided
            return self._validate_grounding_func(map_predicate_value, predicate, value)
        else:
            raise NotImplementedError("No validation function provided.")
            

@dataclass
class Language:
    """
    Encapsulates Vocabulary and Grammar into a single object L = (V, G).
    """
    vocab: Vocabulary
    grammar: Grammar


# Example default vocabulary (train domain)
def default_train_language() -> Language:
    identifiers = {
        "object_identifier": "Train",
        "subobject_identifier": "Car",
        "super_to_sub_predicate": "has_car",
        "subobject_numerating_predicate": "car_num",
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
    return Language(vocab=vocab, grammar=grammar)


if __name__ == "__main__":
    L = default_train_language()