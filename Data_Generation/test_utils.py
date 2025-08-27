from utils import assign_label

def test_assign_label():
    # Define a sample rule and background
    rule = "eastbound(Train):- has_car(Train, Car1), has_payload(Car1, diamond)."
    background = """train1
has_car(train1, car1_1).
car_num(car1_1, 1).
car_color(car1_1, blue).
car_len(car1_1, long).
has_wheel(car1_1, 2).
has_payload(car1_1, diamond).
load_num(car1_1, 3).
car_type(car1_1, mixed).
passenger_num(car1_1, 9).
has_car(train1, car1_2).
car_num(car1_2, 2).
car_color(car1_2, green).
car_len(car1_2, short).
has_wheel(car1_2, 2).
has_payload(car1_2, golden_vase).
load_num(car1_2, 1).
car_type(car1_2, mixed).
passenger_num(car1_2, 5).

"""

    # Call the assign_label function
    label = assign_label(rule, background)

    # Print the result
    print(f"Assigned label: {label}")

if __name__ == "__main__":
    test_assign_label()