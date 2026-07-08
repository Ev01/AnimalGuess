#import math
import json

ANIMALS_FILENAME = "animals.json"

ANS_NO = 0
ANS_YES = 1
ANS_MAYBE = 2

def get_question_usefulness(animal_questions, question):
    num_true = 0
    num_false = 0
    num_unsure = 0

    for qs in animal_questions.values():
        match qs.get(question, None):
            case True:
                num_true += 1
            case False:
                num_false += 1
            case None:
                num_unsure += 1

    # If you have any animals where the question is unsure, you might still be
    # able to rule out the animals that are known true or false
    unsure_boost = 1 if (num_true + num_false) * num_unsure else 0
    """
    print(f"{num_true=}, {num_false=}")
    #total = len(animal_questions) # number of animals in total
    
    # Value of 0.5 means this question splits the animals half-half. Value of 0
    # means this question does not split the animals at all.
    gini = 1 - (num_true / total) ** 2 - (num_false / total) ** 2
    return gini
    """
    #total = num_true + num_false + num_unsure
    # Higher is better
    return num_true * num_false + unsure_boost

    #return num_true + num_false 


def get_all_questions(animal_questions):
    all_questions = set()
    for qs in animal_questions.values():
        for q in qs.keys():
            all_questions.add(q)

    return all_questions


def pick_best_question(animal_questions, exclude_questions=set()):
    all_questions = get_all_questions(animal_questions)
    all_questions -= exclude_questions

    #print("All questions:")
    #print(all_questions)
    best_usefulness = 0
    best_question = ""
    print("Usefulness:")
    for q in all_questions:
        usefulness = get_question_usefulness(animal_questions, q)
        print(f"{q}: {usefulness}")
        if usefulness > best_usefulness:
            best_usefulness = usefulness
            best_question = q

    return best_question, best_usefulness


def ask_question(q):
    while True:
        ans_str = input(q + " (y/n) ")
        if ans_str == "y" or ans_str == "yes":
            return True
        elif ans_str == "n" or ans_str == "no":
            return False
        else:
            print("Please answer with yes or no")

def ask_question_with_maybe(q):
    while True:
        ans_str = input(q + " (y/n/m) ")
        if ans_str == "y" or ans_str == "yes":
            return ANS_YES
        elif ans_str == "n" or ans_str == "no":
            return ANS_NO
        elif ans_str == "m" or ans_str == "mabye":
            return ANS_MAYBE
        else:
            print("Please answer with yes, no, or maybe.")

"""
def get_question_true_animals(animal_questions, question):
    true_keys = set()
    for animal in animal_questions:
        ans = animal_questions[animal].get(question, None)
        if ans == True:
            true_keys.add(animal)

    return true_keys

def get_question_false_animals(animal_questions, question):
    false_keys = set()
    for animal in animal_questions:
        ans = animal_questions[animal].get(question, None)
        if ans == False:
            false_keys.add(animal)

    return false_keys
"""

def get_animals_with_question_ans(animal_questions, question, desired_ans):
    keys = set()
    for animal in animal_questions:
        ans = animal_questions[animal].get(question, None)
        if ans == desired_ans:
            keys.add(animal)

    return keys


def celebrate_win():
    print("I guessed your animal!")


def main():
    with open(ANIMALS_FILENAME, "r") as f:
        animal_questions = json.load(f)

    curr_aq = animal_questions.copy()
    already_asked = {}
    maybe_questions = set()

    while len(curr_aq) > 1:
        q, usefulness = pick_best_question(
                curr_aq, exclude_questions=set(already_asked) | maybe_questions)
        if usefulness == 0:
            break
        #print(f"The best question was: {q}\n with a usefulness index of {usefulness}")
        ans = ask_question_with_maybe(q)

        if ans == ANS_MAYBE:
            maybe_questions.add(q)
        else:
            ans = bool(ans)
            already_asked[q] = ans
            anims_to_remove = get_animals_with_question_ans(curr_aq, q, not ans)
            for key in anims_to_remove:
                curr_aq.pop(key)

    # There are no more useful questions. We have three guesses to choose an
    # animal.
    animals_left = tuple(curr_aq.keys())
    did_guess_animal = False
    players_animal = ""
    print(animals_left)
    for anim in animals_left[:3]:
        ans = ask_question(f"is your animal a {anim}?")
        if ans == True:
            celebrate_win()
            did_guess_animal = True
            players_animal = anim

    if not did_guess_animal:
        # Animal has still not been guessed
        players_animal = input("I could not guess your animal. What is it? ")
        comp_animal = animals_left[-1]
        new_question = input(f"Please type a question that would differentiate a {players_animal} from a {comp_animal}: ")
        new_question_ans = ask_question(f"And how would you answer this question for a {players_animal} (yes/no)? ")

        already_asked[new_question] = new_question_ans
        animal_questions[comp_animal][new_question] = not new_question_ans

    animal_questions[players_animal] = already_asked

    print("Game finished. Animals left:")
    print(curr_aq.keys())

    print()
    print("New animals:")
    print(json.dumps(animal_questions, indent=2))

    with open(ANIMALS_FILENAME, "w") as f:
        json.dump(animal_questions, f, indent=2)
        



if __name__ == "__main__":
    main()
