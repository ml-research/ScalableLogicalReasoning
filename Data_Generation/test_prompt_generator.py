from prompt_generator import PromptGenerator
from language import Grammar, Language, Vocabulary

def test_generate_prompt():
    # Define a sample background, positives, negatives, and language
    background = """
pos(train0).
has_car(train0, car0_1).
car_num(car0_1, 1).
car_color(car0_1, white).
car_len(car0_1, short).
has_wall(car0_1, full).
    """
    positives = "pos(train0)."
    negatives = "neg(train1)."

    # Mock language object
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

        
    def validate_grounding(map_predicate_value, predicate, value) -> bool:

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
    vocab = Vocabulary(identifiers=identifiers,predicates=predicates, predicate_arg_types=predicate_arg_types, constants=constants)

    language = Language(vocab=vocab, grammar=grammar)

    # Initialize PromptGenerator
    prompt_generator = PromptGenerator()

    # Generate prompt
    prompt = prompt_generator.generate_prompt(background, positives, negatives, language)

    # Print the generated prompt
    print("Generated Prompt:")
    print(prompt)

if __name__ == "__main__":
    test_generate_prompt()