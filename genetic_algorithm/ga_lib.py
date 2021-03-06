import numpy as np
import time
from GeneticAlgorithm import Individual



class null_crossover(object):
    def __init__(self, *args, **kwargs):
        self.num_xovers = 0
        self.parent_mean = 0
        self.child_mean = 0
        self.moves = 0
        self.delta_cost = 0
        self.nary = 1

    def __call__(self, ga, individuals, selection_ids):
        return [Individual(individuals[s].chromosome.copy()) for s in selection_ids]

"""
    Mutators
"""

def null_mutation(ga, selection_ids, children):
    return children

"""
    Selection Methods
"""
def null_selection(ga, individuals, size, verbose=False):
    selection_ids = xrange(min(size, len(individuals)))
    return selection_ids

def tournament_select(tournament_size, probability=1.0, maximize=False):
    """
        probability that the best will be chosen.
    """
    def _tournament_select(ga, individuals, size, verbose=False):
        assert(tournament_size > 0)
        assert(len(individuals) >= tournament_size)
        selection_ids = list()
        while len(selection_ids) < size:
            tournament = set()
            selectable = list(range(len(individuals)))
            while len(tournament) < tournament_size:
                index = int( round(ga.random_gen.random() * (len(selectable) - 1) ) )
                tournament.add(selectable[index])
                del selectable[index]

            if verbose:
                print 'Competitors', tournament
            tournament_map = [(individuals[id_], id_) for id_ in tournament]

            _max = max(tournament_map, key=lambda x: x[0].fitness)
            _min = min(tournament_map, key=lambda x: x[0].fitness)

            if maximize:
                if ga.random() < probability:
                    winner = _max
                else:
                     winner = _min
            else:
                if ga.random() < probability:
                    winner = _min
                else:
                    winner = _max

            if verbose:
                print 'Winner', winner[1]
            selection_ids.append(winner[1])

        return selection_ids
    return _tournament_select

"""
    Replacement Strategies
"""

def replace_and_truncate(ga, selection_ids, children):
    ga.next_generation.extend(children)
    if ga.population_size < len(ga.next_generation):
        ga.next_generation = ga.next_generation[:ga.population_size]
    return len(ga.next_generation) == ga.population_size

def replace_fraction(fraction, maximize=False):
    def _replace_fraction(ga, selection_ids, children):
        length = int(ga.population_size * fraction)
        ga.next_generation.extend(children)
        if length >= len(ga.next_generation):
            ga.next_generation = ga.next_generation[:length]
            ga.next_generation.extend(sorted(ga.individuals, reverse=maximize, key=lambda x: x.fitness)[:ga.population_size - length])
            return False
        else:
            return True
    return _replace_fraction


def replace_all_but(elite_num, maximize=False):
    assert(elite_num >= 0)
    def _replace_all_but(ga, selection_ids, children):
        ga.next_generation.extend(children)
        length = len(ga.next_generation)
        replace_length = ga.population_size - elite_num
        if length >= replace_length:
            ga.next_generation = ga.next_generation[:replace_length]
            ranked = sorted(ga.individuals, reverse=maximize, key=lambda x: x.fitness)
            ga.next_generation.extend(ga.individuals[:elite_num])
            return True
        else:
            return False
    return _replace_all_but


"""
    Stop Criteria
"""

def stop_count_generations(limit):
    def _stop_count_generations(ga):
        return ga.generation > limit
    return _stop_count_generations


def stop_sum_difference(diff):
    def _stop_sum_difference(ga):
        costs = [s.fitness for s in ga.individuals]
        mean = np.mean(costs)
        sum_diff = sum([abs(c - mean) for c in costs])
        return sum_diff <= diff
    return _stop_sum_difference


def stop_deviation(limit):
    def _stop_deviation(ga):
        fitness = [x.fitness for x in ga.individuals]
        mean = np.mean(fitness)
        dev = (mean - min(fitness)) + (max(fitness) - mean)
        if dev <= limit:
            print mean, dev, limit, min(fitness), max(fitness)
            return True
        else:
            return False
    return _stop_deviation

class StopBestNonImproving(object):
    def __init__(self, limit, threshold, population_reference=np.mean):
        self.limit = limit
        self.count = 0
        self.previous = None
        self.threshold=threshold
        self.choice_fn = population_reference

    def __call__(self, ga):
        fitness = self.choice_fn([s.fitness for s in ga.individuals])
        if self.previous and abs(fitness - self.previous) <= self.threshold:
            self.count += 1
        self.previous = fitness
        return self.count >= self.limit
