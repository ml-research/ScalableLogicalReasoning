import unittest
from language import Grammar, Language, Vocabulary
from background_generator import BackgroundGenerator

class TestBackgroundGenerator(unittest.TestCase):

    def setUp(self):
        # Define a sample language for testing
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

        self.language = Language(vocab=vocab, grammar=grammar)

    def test_generate_uniform_background(self):
        background_generator = BackgroundGenerator(language=self.language, B_pi='uniform')
        rule = 'eastbound(Train):- has_car(Train, Car1), car_num(Car1, 2), has_car(Train, Car2), has_wheel(Car2, 3), has_car(Train, Car3), has_wheel(Car3, 2).'
        with open("generated_backgrounds.txt", "w") as f:
            for _ in range(100):  # Generate 100 backgrounds
                background = background_generator.generate_background(rule, 1)
                f.write(background + "\n")

    def test_generate_mirror_background(self):
        background_generator = BackgroundGenerator(language=self.language, B_pi='mirror')
        rule = 'eastbound(Train):- has_car(Train, Car1), car_len(Car1, short),  has_car(Train, Car2), car_color(Car2, white)'
        first_train = '''train0
has_car(train0, car0_1).
car_num(car0_1, 1).
car_color(car0_1, yellow).
car_len(car0_1, long).
has_wheel(car0_1, 3).
has_payload(car0_1, golden_vase).
load_num(car0_1, 3).
car_type(car0_1, mixed).
passenger_num(car0_1, 0).
has_car(train0, car0_2).
car_num(car0_2, 2).
car_color(car0_2, blue).
car_len(car0_2, short).
has_wheel(car0_2, 2).
has_payload(car0_2, barrel).
load_num(car0_2, 1).
car_type(car0_2, mixed).
passenger_num(car0_2, 5).
'''
        with open("generated_mirror_backgrounds.txt", "w") as f:
            for _ in range(1):  # Generate 1 background
                background = background_generator.generate_background(rule, 1, first_sample=first_train )
                f.write(background + "\n")

if __name__ == '__main__':
    unittest.main()
