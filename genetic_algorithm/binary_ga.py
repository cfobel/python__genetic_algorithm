import numpy as np
from path import path
import sys
from GeneticAlgorithm import Individual, GeneticAlgorithm
from ga_lib import *


def stop_count_generations(limit):
    def _stop_count_generations(ga):
        return ga.generation > limit
    return _stop_count_generations


def initialize_strings(length):
    def _initialize_strings(ga):
        for i in range(ga.population_size):
            ga.individuals.append(Individual(
                [int(round(ga.random_gen.frand())) for i in range(length)]))
    return _initialize_strings

def num_ones(ga, needs_calculated):
    for s in needs_calculated:
        s.fitness = sum(s.chromosome) / float(len(s.chromosome))


def bit_flip_mutation(rate):
    def _bit_flip_mutation(ga, selection_ids, children):
        mutants = list()
        for child in children:
            length = len(child.chromosome)
            flips = int(length * rate)
            for i in range(flips):
                index = int(ga.random_gen.frand() * length)
                child.chromosome[index] = 1 - child.chromosome[index]
            mutants.append(child)
        return mutants
    return _bit_flip_mutation

class SinglePointCrossover(object):
    def __init__(self, rate):
        self.nary = 2
        self.rate = rate

    def __call__(self, ga, selection_ids):
        string_1 = ga.individuals[selection_ids[0]]
        string_2 = ga.individuals[selection_ids[1]]
        if ga.random_gen.frand() < self.rate:
            point = int(ga.random_gen.frand() * len(string_1.chromosome))
            child_1_chromosome = string_1.chromosome[:point] + string_2.chromosome[point:]
            child_2_chromosome = string_2.chromosome[:point] + string_1.chromosome[point:]
        else:
            child_2_chromosome = string_2.chromosome[:]
            child_1_chromosome = string_1.chromosome[:]
        return [Individual(child_2_chromosome), Individual(child_1_chromosome)]


if __name__ == "__main__":
    Ga = GeneticAlgorithm(initialize=initialize_strings(50),
                          population_size=80,
                          crossover=SinglePointCrossover(.90),
                          mutate=bit_flip_mutation(.02),
                          select=tournament_select(2, maximize=True),
                          evaluate=num_ones,
                          replace=replace_all_but(1, maximize=True),
                          stop_criteria=stop_count_generations(70),
                          verbose=False, test=True)

    for i, generation in enumerate(Ga):
        num_ones(Ga, Ga.individuals)
        print 'Generation:', i, 'max_fitness:', max(Ga.individuals, key=lambda x: x.fitness).fitness
    fitness = [s.fitness for s in Ga.individuals]
    print 'min %.2f mean %.2f max %.2f' % (min(fitness), np.mean(fitness), max(fitness))


