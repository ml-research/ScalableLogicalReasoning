from evaluate import load
from language import Language
from task_config import TaskConfig
from rule_generator import RuleGenerator
from background_generator import BackgroundGenerator
from validation_program import ValidationProgram
from prompt_generator import PromptGenerator
from utils import assign_label, replace_object_name_with_label_txt

class TaskSynthesiser():
    """
    Synthesises a logical reasoning task consisting of a rule, examples, and a prompt.
    """

    def generate_task(self, language: Language, task_config: TaskConfig):
        """
        Generates a task with background facts, positive/negative examples, and a prompt.
        The number of examples and the rule are determined by the TaskConfig object.
        """

        background = []  # List of facts (without label) for each example
        positive_examples = []  # List of positive labels (e.g. eastbound(train1).)
        negative_examples = []  # List of negative labels (e.g. westbound(train2).)

        rule_generator = RuleGenerator(language=language, Rlen=task_config.Rlen, Rsample=task_config.Rsample)
        background_generator = BackgroundGenerator(language=language, B_pi=task_config.B_pi)
        num_pos, num_neg = task_config.kappa  # Target number of positive/negative examples

        first_sample = ''  # First generated example (used as reference)
        sample_index = 0   # Index for selecting constants

        rule = rule_generator.generate_rule()
        while rule == '':
            rule = rule_generator.generate_rule()
        try_count = 0
        symbolic_judge = load("AIML-TUDA/VerifiableRewardsForScalableLogicalReasoning")

        while len(positive_examples) < num_pos or len(negative_examples) < num_neg:
            # Generate a new background (facts) for the current example
            b = background_generator.generate_background(rule=rule, sample_index=sample_index, first_sample=first_sample)

            # If too many failed attempts or invalid example: reset everything and generate a new rule
            if try_count > 10 or b == '':
                # Reset all relevant variables and generate a new rule
                background = []
                positive_examples = []
                negative_examples = []
                try_count = 0
                sample_index = 0
                first_sample = ''
                rule = rule_generator.generate_rule()
                while rule == '':
                    rule = rule_generator.generate_rule()
                continue

            if first_sample == '':
                first_sample = b  # Store the first example as reference

            # Determine the label (y) and label string (q) for the example
            y, q = assign_label(language=language, rule=rule, background=b, symbolic_judge=symbolic_judge)

            # Extract the label and facts, and add them to the respective lists
            if y == 1 and len(positive_examples) < num_pos:
                whole_program = replace_object_name_with_label_txt(b, q)
                lines = whole_program.strip().splitlines()
                label = lines[0]  # e.g. eastbound(train1).
                facts = "\n".join(lines[1:])  # Only the facts, without the label
                background.append(facts)
                positive_examples.append(label)
                sample_index += 1

            elif y == 0 and len(negative_examples) < num_neg:
                whole_program = replace_object_name_with_label_txt(b, q)
                lines = whole_program.strip().splitlines()
                label = lines[0]  # e.g. westbound(train2).
                facts = "\n".join(lines[1:])
                background.append(facts)
                negative_examples.append(label)
                sample_index += 1

            else:
                try_count += 1  # Failed attempt, increment counter
                continue

        # Create the validation program and the prompt
        program = ValidationProgram(background=background, positives=positive_examples, negatives=negative_examples)
        prompt = PromptGenerator.generate_prompt(background=background, positives=positive_examples, negatives=negative_examples, language=language)

        return rule, program, prompt
