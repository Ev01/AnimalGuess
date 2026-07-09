import json
import argparse
import logging
logger = logging.getLogger(__name__)

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
    #return num_true * num_false + unsure_boost
    return min(num_true, num_false) + unsure_boost

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
    logger.debug("Question usefulness:")
    
    for q in all_questions:
        usefulness = get_question_usefulness(animal_questions, q)
        logger.debug(f"{q}: {usefulness}")
        if usefulness > best_usefulness:
            best_usefulness = usefulness
            best_question = q

    return best_question, best_usefulness


def get_animal_confidence_score(animal_questions, animal, already_answered):
    qs = animal_questions[animal]
    score = 0
    for q in qs:
        if qs[q] == already_answered.get(q, None):
            score += 1

    return score / len(already_answered)



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


def get_animals_with_question_ans(animal_questions, question, desired_ans):
    keys = set()
    for animal in animal_questions:
        ans = animal_questions[animal].get(question, None)
        if ans == desired_ans:
            keys.add(animal)

    return keys


def celebrate_win():
    print("I guessed your animal!")


def play_round():
    with open(ANIMALS_FILENAME, "r") as f:
        animal_questions = json.load(f)

    curr_aq = animal_questions.copy()
    already_asked = {}
    maybe_questions = set()

    while len(curr_aq) > 3:
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

        logger.debug("I have narrowed it down to:")
        for animal in curr_aq.keys():
            logger.debug(animal, get_animal_confidence_score(curr_aq, animal, already_asked))

    # There are no more useful questions. We have three guesses to choose an
    # animal.
    animals_left = list(curr_aq.keys())
    animals_left.sort(reverse=True, key=lambda x: get_animal_confidence_score(curr_aq, x, already_asked))
    did_guess_animal = False
    players_animal = ""
    logger.debug(animals_left)
    for anim in animals_left[:3]:
        ans = ask_question(f"is your animal a {anim}?")
        if ans == True:
            celebrate_win()
            did_guess_animal = True
            players_animal = anim
            break

    if not did_guess_animal:
        # Animal has still not been guessed
        players_animal = input("I could not guess your animal. What is it? ")
        comp_animal = animals_left[0]
        new_question = input(f"Please type a question that would differentiate a {players_animal} from a {comp_animal}: ")
        new_question_ans = ask_question(f"And how would you answer this question for a {players_animal} (yes/no)? ")

        already_asked[new_question] = new_question_ans
        animal_questions[comp_animal][new_question] = not new_question_ans

    animal_questions[players_animal] = already_asked

    print("Game finished.")
    logger.debug("Animals left:")
    logger.debug(animals_left)

    print()
    logger.debug("New animals:")
    logger.debug(json.dumps(animal_questions, indent=2))

    with open(ANIMALS_FILENAME, "w") as f:
        json.dump(animal_questions, f, indent=2)
        

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    logging_level = logging.DEBUG if args.debug else logging.ERROR
    logging.basicConfig(level=logging_level)

    is_playing = True
    while is_playing:
        play_round()
        ans = ask_question("Do you want to play again?")
        if not ans:
            is_playing = False


if __name__ == "__main__":
    main()
