from evaluate import load
import re

from language import Language

def assign_label(language: Language, rule: str, background: str, symbolic_judge = None) -> tuple:
    """
    Assigns a label (positive/negative) to a background using a symbolic judge and a rule.
    Returns (label, label_txt) where label is 1 (positive) or 0 (negative), and label_txt is the label string.
    """
    if symbolic_judge is None:
        symbolic_judge = load("AIML-TUDA/VerifiableRewardsForScalableLogicalReasoning")

    positive_label = language.vocab.identifiers['positive_label']
    negative_label = language.vocab.identifiers['negative_label']

    background = replace_object_name_with_label_txt(background, positive_label).strip() + '\n\n' + f'{negative_label}(non_existing_object).'
    references = [
        {
            "validation_program": background,
            "evaluation_config": {
                "positive_predicate": positive_label,
                "negative_predicate": negative_label
            }
        } 
    ]
    predictions = [rule]

    results = symbolic_judge.compute(predictions=predictions, references=references)
    label = int(results['accuracy'])
  
    label_txt = ''
    if label == 1:
        label_txt = positive_label
    else:
        label_txt = negative_label
    return (label,label_txt)

def replace_object_name_with_label_txt(background: str, label_txt: str) -> str:
    """
    Replaces the first line (object name) in a background string with the specified label.
    Example: replace_object_name_with_label_txt('train1\nhas_car(train1, car1).', 'eastbound') -> 'eastbound(train1).\nhas_car(train1, car1).'
    """
    lines = background.strip().splitlines()
    if not lines:
        return background
    object_name = lines[0].strip().rstrip('.')
    lines[0] = f"{label_txt}({object_name})."
    return "\n".join(lines)

# Utility functions for logic program string processing and label assignment

def extract_predicate_value(text: str, predicate_name: str):
    """
    Extract the value of the second argument for a given predicate in a Prolog-like string.
    Example: extract_predicate_value('has_car(train1, car1).', 'has_car') -> 'car1'
    :param text: The string to search (e.g., 'has_car(train1, car1).').
    :param predicate_name: The predicate to look for (e.g., 'has_car').
    :return: The value of the second argument, or None if not found.
    """
    pattern = rf"{predicate_name}\(([^,]+),\s*([^)]+)\)"
    match = re.search(pattern, text)
    if match:
        return match.group(2)
    return None

def extract_object_name(text: str, predicate: str) -> str:
    """
    Extract the object name (first argument) for a given predicate in a Prolog-like string.
    Example: extract_object_name('has_car(train1, car1).', 'has_car') -> 'train1'
    :param text: The string to search (e.g., 'has_car(train1, car1).').
    :param predicate: The predicate to look for (e.g., 'has_car').
    :return: The value of the first argument, or None if not found.
    """
    pattern = rf"{predicate}\(([^,]+),"
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None