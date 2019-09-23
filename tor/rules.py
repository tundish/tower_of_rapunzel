#!/usr/bin/env python3
# encoding: utf-8

# This file is part of Tower of Rapunzel.
#
# Tower of Rapunzel is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Tower of Rapunzel is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Tower of Rapunzel.  If not, see <http://www.gnu.org/licenses/>.

from collections import namedtuple
from collections import OrderedDict
import random
from collections import namedtuple
import fractions
import itertools
import pprint
import random
import statistics
import sys

from turberfield.dialogue.model import SceneScript

folders = [
    SceneScript.Folder(
        pkg="tor",
        description="",
        metadata={"location": locn},
        paths=[],
        interludes=None
    ) for locn in "BFWHGfBC"
]

tower = 12
playtime_s = 20 * 60
health_max = 100
coins = 0
growth = fractions.Fraction(1, 80)
length = 12
cut = 1
delta = 1

health_drop = fractions.Fraction(health_max / length)
coin_for_hair = 1  # per metre
coin_for_health = fractions.Fraction(1, 40)
growth_for_coin = fractions.Fraction(1, 800)

State = namedtuple(
    "State",
    ["location", "hair_m", "hair_d", "cut_m", "coins_n", "health_n"]
)

def call_rules(folder, index, entities, **kwargs):
    location = folder.metadata["location"]
    rv = folder.metadata.copy()
    length = kwargs.get("hair_m", 12)
    growth = kwargs.get("hair_d", fractions.Fraction(1, 80))
    coins = kwargs.get("coins_n", 0)
    health = kwargs.get("health_n", 100)
    if location == "C":
        # Rapunzel's hair is ?m long. How much do you want to cut?
        # NB: Waiting allows it to grow.
        choice = random.choice([delta, 0 , -delta])
        cut = max(0, kwargs.get("cut", 1) + choice)
        length = max(0, length - cut)
    elif location == "F":
        damage = health_drop * (tower - kwargs.get("hair_m", tower))
        health = max(0, kwargs.get("health_n", 100) - max(0, damage))
        if health == 0:
            return
    elif location == "W":
        coins += coin_for_hair * kwargs.get("cut_m", 1)
    elif location == "H":
        cost = min(
            kwargs.get("coins", 0),
            int((health_max - kwargs.get("health_n", 100)) * coin_for_health)
        )
        coins -= cost
        health += cost / coin_for_health
    elif location == "G":
        choice = random.choice([i * coin_for_hair for i in (0, 1, 2, 5)])
        cost = min(coins, choice)
        coins -= cost
        growth += cost * growth_for_coin
    elif location == "f":
        # Game will check it's possible to get back up.
        pass

    return rv

def operate(folders, coins=coins, cut=cut, growth=growth, health=health_max, length=length):
    for n, folder in enumerate(pathway(folders)):
        locn = folder.metadata["location"]
        if locn == "C":
            # Rapunzel's hair is ?m long. How much do you want to cut?
            # NB: Waiting allows it to grow.
            choice = random.choice([delta, 0 , -delta])
            cut = max(0, cut + choice)
            length = max(0, length - cut)
        elif locn == "F":
            damage = health_drop * (tower - length)
            health = max(0, health - max(0, damage))
            if health == 0:
                return
        elif locn == "W":
            coins += coin_for_hair * cut
        elif locn == "H":
            cost = min(coins, int((health_max - health) * coin_for_health))
            coins -= cost
            health += cost / coin_for_health
        elif locn == "G":
            choice = random.choice([i * coin_for_hair for i in (0, 1, 2, 5)])
            cost = min(coins, choice)
            coins -= cost
            growth += cost * growth_for_coin
        elif locn == "f":
            # Game will check it's possible to get back up.
            pass

        length += length * growth
        yield State(locn, int(length), cut, coins, int(health))

if __name__ == "__main__":
    n_runs = 5000
    runs = [list(operate(folders)) for i in range(n_runs)]
    ranking = sorted(runs, key=lambda x: x[-1].coins_n, reverse=True)
    outcomes = [i[-1].coins_n for i in ranking]
    pprint.pprint(ranking[0])
    try:
        print(
            *statistics.quantiles(outcomes, n=n_runs // 4, method="inclusive"),
            sep="\n",
            file=sys.stderr
        )
    except AttributeError:
        pass
    # Bronze: 20, Silver: 25: Gold: 30
