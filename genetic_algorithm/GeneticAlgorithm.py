#!/usr/bin/env python

import random

class Individual(object):
    id_counter = 0
    def __init__(self, chromosome, id_=None, fitness=None):
        self.chromosome = chromosome
        self.fitness = fitness
        if id_ is None:
            self.id_ = Individual.id_counter
            Individual.id_counter += 1
        else:
            self.id_ = id_

class GeneticAlgorithm(object):
    def __init__(self, initialize, population_size, crossover,
                mutate, select, evaluate, replace, stop_criteria,
                maximize=False, verbose=True, test=True, random_generator=random):

        self.random_gen = random_generator
        self.population_size = population_size
        self.individuals = list()
        self.next_generation = list()
        self.generation = -1
        self.selection = 0
        self.maximize = maximize

        self._mutate = mutate
        self._crossover = crossover
        self._select = select
        self._evaluate = evaluate
        self._replace = replace
        self._stop_criteria = stop_criteria
        self._initialize = initialize

        self.verbose = verbose
        self.test = test

    def verify(self):
        assert(not self.individuals or all([isinstance(s, Individual) for s in self.individuals]))
        assert(not self.next_generation or all([isinstance(s, Individual) for s in self.next_generation]))
        assert(self.population_size > 0)
        assert(self.generation >= -1)
        assert(self.selection >= 0)
        assert(self._replace)
        assert(self._stop_criteria)
        assert(self._initialize)


    def _log(self):
        print '[Genetic Algorithm]: population_size', self.population_size
        print '[Genetic Algorithm]: individuals fitness', [s.fitness for s in self.individuals]
        print '[Genetic Algorithm]: next_generation fitness', [s.fitness for s in self.next_generation]
        print '[Genetic Algorithm]: generation', self.generation
        print '[Genetic Algorithm]: selection', self.selection

        print '[Genetic Algorithm]: verbose', self.verbose
        print '[Genetic Algorithm]: test', self.test

        print '[Genetic Algorithm]: mutate', self._mutate
        print '[Genetic Algorithm]: select', self._select
        print '[Genetic Algorithm]: evaluate', self._evaluate
        print '[Genetic Algorithm]: crossover', self._crossover
        print '[Genetic Algorithm]: replace', self._replace
        print '[Genetic Algorithm]: stop_criteria', self._stop_criteria
        print '[Genetic Algorithm]: initialize', self._initialize


    def initialize(self):
        if self.verbose:
            print '[Genetic Algorithm] initialize:'
        self._initialize(self)
        if self.test:
            self._test_initialize()

    def _test_initialize(self):
        assert(self.population_size == len(self.individuals))
        assert(all([isinstance(s, Individual) for s in self.individuals]))
        assert(len(self.next_generation) == 0)
        assert(self.generation == -1)
        assert(self.selection == 0)

    def crossover(self, selection_ids):
        if self.verbose:
            print '[Genetic Algorithm] crossover: selection_ids', selection_ids
        children = self._crossover(self, self.individuals, selection_ids)
        if self.test:
            self._test_crossover(selection_ids, self.individuals, children)
        return children

    def _test_crossover(self, individuals, selection_ids, children):
        assert(children)

    def select(self, size):
        if self.verbose:
            print '[Genetic Algorithm] selection: size', size
        selection_ids = self._select(self, self.individuals, size)
        if self.test:
            self._test_select(self.individuals, size, selection_ids)
        return selection_ids

    def _test_select(self, individuals, size, selection_ids):
        assert(size > 0)
        assert(selection_ids)
        assert(all([type(s) == int for s in selection_ids]))

    def stop_criteria(self):
        if self.verbose:
            print '[Genetic Algorithm] stop_criteria:'
        do_stop = self._stop_criteria(self)
        if self.test:
            self._test_stop_criteria(do_stop)
        return do_stop

    def _test_stop_criteria(self, do_stop):
        pass
        #assert(do_stop == self._stop_criteria(self))

    def evaluate(self, needs_evaluated):
        if self.verbose:
            print '[Genetic Algorithm] evaluate:'
        evaled = self._evaluate(self, needs_evaluated)
        if self.test:
            self._test_evaluate(needs_evaluated)
        return evaled

    def _test_evaluate(self, needs_evaluated):
        assert(all([s.fitness is not None for s in needs_evaluated]))

    def replace(self, selection_ids, children):
        if self.verbose:
            print '[Genetic Algorithm] replace: selection_ids', selection_ids
        do_select = self._replace(self, selection_ids, children)
        if self.test:
            self._test_replace(selection_ids, children, do_select)
        return do_select

    def _test_replace(self, selection_ids, children, do_select):
        pass

    def mutate(self, selection_ids, children):
        if self.verbose:
            print '[Genetic Algorithm] mutate: selection_ids', selection_ids
        mutants = self._mutate(self, selection_ids, children)
        if self.test:
            self._test_mutate(selection_ids, children, mutants)
        return mutants

    def _test_mutate(self, selection_ids, children, mutants):
        pass

    def __iter__(self):
        self.initialize()
        if self.verbose:
            self._log()

        yield self
        while True: # Generation Loop
            self.generation += 1
            self.evaluate(self.individuals)
            if self.stop_criteria():
                break

            self.selection = 0
            while True: # Selection Loop
                selection = self.select(self._crossover.nary)
                children = self.crossover(selection)
                children = self.mutate(selection, children)
                if self.replace(selection, children):
                    break
                self.selection += 1
            # end Selection Loop

            yield self
            if self.test:
                self._test_iter()

            self.individuals = self.next_generation
            self.next_generation = list()
            # end Generation Loop

    def _test_iter(self):
        self.verify()

