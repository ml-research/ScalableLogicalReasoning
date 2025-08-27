import unittest
from language import Grammar, Language, Vocabulary
from background_generator import BackgroundGenerator

class TestCustomBackgroundGenerator(unittest.TestCase):
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
            'Car': ['car0_1', 'car0_2', 'car1_1', 'car2_1'],
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
            return True  # For testing, allow all groundings
        grammar = Grammar(_validate_grounding_func=validate_grounding)
        vocab = Vocabulary(identifiers=identifiers, predicates=predicates, predicate_arg_types=predicate_arg_types, constants=constants)
        self.language = Language(vocab=vocab, grammar=grammar)

    def test_generate_custom_background_probabilities(self):
        # Define a probability distribution for car_color
        B_pi = {
            'car_color': {'red': 0.8, 'blue': 0.1, 'green': 0.1, 'yellow': 0.0, 'white': 0.0}
        }
        generator = BackgroundGenerator(language=self.language, B_pi=B_pi)
        # Generate many samples and check the color distribution
        color_counts = {color: 0 for color in B_pi['car_color']}
        for _ in range(1000):
            sample = generator.generate_custom_background(language=self.language, sample_index=0)
            for color in B_pi['car_color']:
                if f'car_color(car0_1, {color})' in sample:
                    color_counts[color] += 1
        # Red should be much more frequent than blue or green
        self.assertGreater(color_counts['red'], 600)
        self.assertLess(color_counts['blue'], 200)
        self.assertLess(color_counts['green'], 200)
        self.assertEqual(color_counts['yellow'], 0)
        self.assertEqual(color_counts['white'], 0)
        print("Color counts:", color_counts)

if __name__ == "__main__":
    unittest.main()
