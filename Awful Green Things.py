#!/usr/bin/env python
'''
An implementation of the lengthy epilogue of
the board game 'Awful Green Things from Outer Space'.
It is recommended you familiarise yourself
with it before using this tool.

Code by IFcoltransG some years ago on a mobile phone
Light edits provided by IFcoltransG more recently
'''

from typing import Union, Callable, Literal, TypeAlias

Flag: TypeAlias = Union[Literal["continue"], int]

try:
    from random import SystemRandom
    #cryptographically secure but wholly unnecessary
    #for extra guarantees of fairness
    random = SystemRandom()
except Exception:
    print("Falling back to non-secure randomness")
    import random

def dice(number_of_dice=1) -> int:
    """
    rolls a number of dice and adds result
    """
    rolls = (random.randrange(1, 7) for i in range(number_of_dice))
    return sum(rolls)


class Crewmate:
    """
    Class for crewmates
    """
    def __init__(self, con: int, dice: int, special : Union[str, None] = None):
        self.con = con
        self.dice = dice
        self.special = special

class Ship:
    """
    Class for ships
    """
    def __init__(self, crew: list[Crewmate]):
        self.location = 1
        self.crew = crew
        self.needs_provisions = False
        self.provisions = 0
    def get_score(self) -> int:
        total = 0
        for crewmate in self.crew:
            if crewmate.special is None:
                #mascot and robot don't count to final score
                total += crewmate.con #sum of constitutions
        return total

class Event:
    """
    this class is used for creating the event functions
    e.g. #1 has a decision so we assign location 1 the function returned by Event.decision()
    then run the created function whenever we end up at 1
    """

    @staticmethod
    def randomised(loc1: int, loc2: int, threshold: int) -> Callable[[Ship], Flag]:
        #generates functions that can switch you to
        #one of two locations randomly
        def random_loc(ship):
            #the locations and probability are in the closure
            new_loc = loc1 if dice() <= threshold else loc2
            ship.location = new_loc
            return "continue"
        new_name = f"{random_loc.__name__} {loc1} or {loc2}"
        #sets function name to be more meaningful
        random_loc.__name__ = new_name
        return random_loc
    @staticmethod

    def decision(loc1: int, loc2: int, description1: str, description2: str) -> Callable[[Ship], Flag]:
        def decide_loc(ship):
            if ship.needs_provisions:
                print("You need provisions in", ship.provisions, "years.")
            else:
                print("You have enough provisions for now.")
            print(f"You have {len(ship.crew)} crewmembers,"
                f" for a total score of {ship.get_score()}!")
            #ship state reported
            print("Choose:")
            print(f"{loc1}: {description1}")
            print(f"{loc2}: {description2}")
            while True:
                #validation
                try:
                    last_input = int(input().strip())
                    if last_input in (loc1, loc2):
                        break
                except ValueError:
                    print("enter a proper number")
            ship.location = last_input
            return "continue"
        new_name = f"{decide_loc.__name__} {loc1} or {loc2}"
        #gives generated function meaningful __name__
        decide_loc.__name__ = new_name
        return decide_loc

    @staticmethod
    def disease(*args, **kwargs) -> Callable[[Ship], Flag]:
        continued = Event.randomised(*args, **kwargs)
        #continued is a function
        #if disease resisted, boat moves on randomly
        all_dead = Event.death("Everyone got Gravy Flu and died.")
        #all_dead is a function
        def gravy_flu(ship):
            for person in ship.crew:
                if person.con <= dice(4):
                    ship.crew.remove(person)
            if not ship.crew:
                return all_dead(ship)
            return continued(ship)
        return gravy_flu

    @staticmethod
    def fight(refill_loc: int, failure_loc: int) -> Callable[[Ship], Flag]:
        all_dead = Event.death("Your aliens fought an alien incursion. The aliens won. The other aliens, that is; all your crew are dead.")
        def native_battle(ship):
            native_dice = dice() #1d6
            native_atk = dice(native_dice) #(1d6)d6
            crew_dice = sum(person.dice
                            for person
                            in ship.crew)
            crew_atk = dice(crew_dice)
            if native_atk >= crew_atk:
                dead = random.choice(ship.crew)
                ship.crew.remove(dead)
                if not ship.crew:
                    return all_dead(ship)
                ship.location = failure_loc
            ship.location = refill_loc
            return "continue"
        return native_battle

    @staticmethod
    def refill(*args, **kwargs) -> Callable[[Ship], Flag]:
        continued = Event.randomised(*args, **kwargs)
        def resupply(ship):
            ship.needs_provisions = False
            return continued(ship)
        return resupply

    @staticmethod
    def low_provisions(*args, **kwargs) -> Callable[[Ship], Flag]:
        no_food = Event.death("You ran out of hard tack and swill. Your crew starved to death.")
        continued = Event.decision(*args, **kwargs)
        def provisions_low(ship):
            if ship.needs_provisions:
                return no_food(ship)
            ship.needs_provisions = True
            ship.provisions = 2
            return continued(ship)
        return provisions_low

    @staticmethod
    def death(message) -> Callable[[Ship], Flag]:
        def loss(ship):
            print("ship lost!")
            print(message)
            #game end functions return a score
            return 0
        loss.__name__ += ": " + message
        #more meaningful function name
        return loss

    @staticmethod
    def snudl() -> Callable[[Ship], Flag]:
        def win(ship):
            #at least one crew made in to Snudl-1
            print("A winner is you! Your boat returned safely home.")
            score = ship.get_score()
            print("Total crew left for this boat:",score)
            #return score rather than "continue"
            #because game has ended
            return score
        return win

    @staticmethod
    def years(year_number: int, *args, **kwargs) -> Callable[[Ship], Flag]:
        no_food = Event.death("Out of food")
        continued = Event.randomised(*args, **kwargs)
        def year_decrement(ship):
            ship.provisions -= year_number
            if ship.needs_provisions and ship.provisions <= 0:
                return no_food(ship)
            return continued(ship)
        new_name = f"years_{year_number}"
        year_decrement.__name__ = new_name
        return year_decrement

#initialises location list to the appropriate events
#as per Awful Green Things epilogue
locations = {
    1: Event.decision(7, 3, "straight for Snudl-1", "to last planet"),
    2: Event.years(1, 7, 8, 3),
    3: Event.randomised(4, 6, 4),
    4: Event.decision(8, 5, "run from inhabitants", "fight"),
    5: Event.fight(6, 4),
    6: Event.refill(2, 12, 4),
    7: Event.years(2, 13, 14, 4),
    8: Event.randomised(9, 10, 3),
    9: Event.randomised(2, 11, 3),
    10: Event.randomised(8, 15, 3),
    11: Event.death("spaghettified by black hole"),
    12: Event.snudl(),
    13: Event.randomised(6, 15, 3),
    14: Event.low_provisions(2, 3, "go for snudl", "try to restock at a previous planet"),
    15: Event.disease(6, 7, 3),
}

def in_int(msg: str) -> int:
    '''
    validates integer from user input
    '''
    while True:
        try:
            num = int(input(msg).strip())
            if num < 1:
                print("A positive integer please!")
            else:
                # valid number
                return num
        except ValueError:
            print("That's not a number :(")

while __name__ == "__main__":
    score = 0 #total constitution of crew that survive the return to Snudl-1
    boats = in_int("How many boats? ")

    for boat in range(boats):
        print("Boat",str(boat+1))
        crew_num = in_int("How many crew are flying today? ")
        boat_crew: list[Crewmate] = []

        for i in range(crew_num):
            print(f"Ship {boat+1}: crew {i+1} of {crew_num}")
            is_robo = "y" == input("Is this crew member a robot or mascot? y/N  ").casefold().strip()
            #n is default (no validation)
            con = in_int("How much constitution does this crew member have? ")
            attack = in_int("How many attack dice? ")

            print(f"Successfully input a {'' if is_robo else 'non-'}robot/mascot.")
            print(f"Con: {con}, Atk: {attack}")
            boat_crew.append(Crewmate(con, attack, ("special" if is_robo else None)))
            print()

        boat = Ship(boat_crew)
        continue_flag = "continue"

        while continue_flag == "continue":
            print("@", boat.location)
            location_function = locations[boat.location]
            continue_flag = location_function(boat)

        #continue_flag must now contain a score
        #rather than "continue"
        assert isinstance(continue_flag, int)
        this_boat_score = continue_flag
        assert this_boat_score >= 0

        score += this_boat_score
        print("New score:", score)

    print("Final score:", score)

    if input("Play again? y/N ").casefold().strip() != "y":
        break
