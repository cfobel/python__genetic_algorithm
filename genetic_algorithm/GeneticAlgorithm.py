#!/usr/bin/env python

import random


class Individual(object):
    id_counter = 0
    def __init__(self, chromosome, fitness=None, id_=None):
        self.chromosome = chromosome
        self.fitness = fitness
        if id_ is None:
            self.id_ = Individual.id_counter
            Individual.id_counter += 1
        else:
            self.id_ = id_

#TODO simplify this.
# push some functionality into the Ga.run loop method
# consider breaking the loops in selection loop and
# Generation loop to configure.
def SimpleRunLoop(Ga):
    Ga.initialize()
    if Ga.verbose:
        Ga.log()

    yield Ga

    while True: # Generation Loop
        Ga.generation += 1
        Ga.listener(Ga, SimpleRunLoop)
        Ga.evaluate(Ga.individuals)
        if Ga.stop_criteria():
            break

        Ga.selection = 0
        while True: # Selection Loop
            selection = Ga.select(Ga._crossover.nary)
            children = Ga.crossover(selection)
            children = Ga.mutate(selection, children)
            if Ga.replace(selection, children):
                break
            Ga.selection += 1
        # end Selection Loop

        yield Ga
        if Ga.test:
            Ga._test_iter()

        Ga.individuals = Ga.next_generation
        Ga.next_generation = list()
    # end Generation Loop


class GeneticAlgorithm(object):
    def __init__(self, initialize, population_size, crossover,
                mutate, select, evaluate, replace, stop_criteria,
                runloop=SimpleRunLoop, listener=None,
                maximize=False, verbose=True,
                test=True, seed=0):

        random.seed(seed)
        self.init_seed = seed
        self.random_gen = random
        self.population_size = population_size
        self.individuals = list()
        self.next_generation = list()
        self.generation = -1
        self.selection = 0
        self.maximize = maximize
        self.listener = listener

        self.data_map = dict(mutation=dict(),
                             crossover=dict(),
                             selection=dict(),
                             replication=dict(),
                             evaluation=dict(),
                             stop_criteria=dict(),
                             initialize=dict(),
                             run_loop=dict())

        self._runloop = runloop
        self._mutate = mutate
        self._crossover = crossover
        self._select = select
        self._evaluate = evaluate
        self._replace = replace
        self._stop_criteria = stop_criteria
        self._initialize = initialize

        self.verbose = verbose
        self.test = test

    def random(self):
        return self.random_gen.random()

    def callback(self, caller, *args, **kwargs):
        self.__log('Callback triggered', caller)
        if self.listener:
            self.listener(caller, *args, **kwargs)

    def verify(self):
        assert(not self.individuals or all(
            [isinstance(s, Individual) for s in self.individuals]))
        assert(not self.next_generation or all([
            isinstance(s, Individual) for s in self.next_generation]))
        assert(self.population_size > 0)
        assert(self.generation >= -1)
        assert(self.selection >= 0)
        assert(self._replace)
        assert(self._stop_criteria)
        assert(self._initialize)

    def __log(self, *args, **kwargs):
        if self.verbose:
            print('[' + self.__class__.__name__ + ']:' + ','.join(
                map(str, args)))

    def _log(self):
        self.__log('population size', self.population_size)
        self.__log('individuals fitness',
                [s.fitness for s in self.individuals])
        self.__log('next generation fitness',
            [s.fitness for s in self.next_generation])
        self.__log('generation', self.generation)
        self.__log('selection', self.selection)
        self.__log('verbose', self.verbose)
        self.__log('test', self.test)
        self.__log('mutate', self._mutate)
        self.__log('select', self._select)
        self.__log('evaluate', self._evaluate)
        self.__log('crossover', self._crossover)
        self.__log('replace', self._replace)
        self.__log('stop criteria', self._stop_criteria)
        self.__log('initialize', self._initialize)

    def initialize(self):
        if self.verbose:
            self.__log("initialize")
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
            self.__log('crossover: selection ids', selection_ids)
        children = self._crossover(self, self.individuals, selection_ids)
        if self.test:
            self._test_crossover(selection_ids, self.individuals, children)
        return children

    def _test_crossover(self, individuals, selection_ids, children):
        assert(children)

    def select(self, size):
        if self.verbose:
            self.__log('selection: size', size)
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
            self.__log("stop criteria")
        do_stop = self._stop_criteria(self)
        if self.test:
            self._test_stop_criteria(do_stop)
        return do_stop

    def _test_stop_criteria(self, do_stop):
        pass
        #assert(do_stop == self._stop_criteria(self))

    def evaluate(self, needs_evaluated):
        if self.verbose:
            self.__log("evaluate")
        evaled = self._evaluate(self, needs_evaluated)
        if self.test:
            self._test_evaluate(needs_evaluated)
        return evaled

    def _test_evaluate(self, needs_evaluated):
        assert(all([s.fitness is not None for s in needs_evaluated]))

    def replace(self, selection_ids, children):
        if self.verbose:
            self.__log('replace: selection ids', selection_ids)
        do_select = self._replace(self, selection_ids, children)
        if self.test:
            self._test_replace(selection_ids, children, do_select)
        return do_select

    def _test_replace(self, selection_ids, children, do_select):
        pass

    def mutate(self, selection_ids, children):
        if self.verbose:
            self.__log('mutate: selection ids', selection_ids)
        mutants = self._mutate(self, selection_ids, children)
        if self.test:
            self._test_mutate(selection_ids, children, mutants)
        return mutants

    def _test_mutate(self, selection_ids, children, mutants):
        pass

    def __iter__(self):
        return self.runloop()

    def runloop(self):
        return self._runloop(self)

    def run(self):
        for ga in self:
            pass

    def _test_iter(self):
        self.verify()
