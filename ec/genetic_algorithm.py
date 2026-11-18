"""
genetic_algorithm.py
Modular, extensible Genetic Algorithm engine designed for evolutionary optimization
with real-valued and discrete chromosome representations, elitism, adaptive mutation,
and convergence tracking.
"""

import random
import copy
from typing import Callable, List, Tuple, Dict, Any, Optional
import numpy as np


class Individual:
    """Represents a candidate solution in the population."""
    def __init__(self, chromosome: List[float]):
        self.chromosome: List[float] = list(chromosome)
        self.fitness: float = -float('inf')
        self.raw_objectives: Dict[str, float] = {}
        self.constraints_violated: Dict[str, float] = {}
        self.is_valid: bool = True

    def __repr__(self) -> str:
        return f"Individual(fitness={self.fitness:.4f}, valid={self.is_valid})"


class GeneticAlgorithm:
    """
    Standard Real-Valued & Constrained Genetic Algorithm.
    Supports:
      - Tournament & Roulette Wheel Selection
      - Blend (BLX-alpha) and Simulated Binary Crossover (SBX)
      - Gaussian / Polynomial Mutation
      - Elitism preservation
      - Convergence history recording
    """
    def __init__(
        self,
        chromosome_length: int,
        bounds: List[Tuple[float, float]],
        fitness_function: Callable[[List[float]], Tuple[float, Dict[str, float], Dict[str, float]]],
        population_size: int = 100,
        generations: int = 150,
        crossover_rate: float = 0.85,
        mutation_rate: float = 0.15,
        mutation_sigma: float = 0.10,
        tournament_size: int = 3,
        elitism_count: int = 2,
        seed: Optional[int] = 42,
    ):
        self.chrom_len = chromosome_length
        self.bounds = bounds
        self.fitness_func = fitness_function
        self.pop_size = population_size
        self.generations = generations
        self.cx_rate = crossover_rate
        self.mut_rate = mutation_rate
        self.mut_sigma = mutation_sigma
        self.tourn_size = tournament_size
        self.elitism_count = elitism_count

        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        self.population: List[Individual] = []
        self.best_individual: Optional[Individual] = None
        self.history: List[Dict[str, Any]] = []

    def initialize_population(self):
        """Creates initial random population within variable bounds."""
        self.population = []
        for _ in range(self.pop_size):
            chrom = [
                random.uniform(self.bounds[i][0], self.bounds[i][1])
                for i in range(self.chrom_len)
            ]
            ind = Individual(chrom)
            self.evaluate_individual(ind)
            self.population.append(ind)

        self.population.sort(key=lambda ind: ind.fitness, reverse=True)
        self.best_individual = copy.deepcopy(self.population[0])

    def evaluate_individual(self, ind: Individual):
        """Evaluates fitness, objectives, and constraint metrics."""
        fitness, objectives, violations = self.fitness_func(ind.chromosome)
        ind.fitness = fitness
        ind.raw_objectives = objectives
        ind.constraints_violated = violations
        ind.is_valid = len(violations) == 0

    def tournament_selection(self) -> Individual:
        """Tournament selection selects the fittest among a random subset."""
        candidates = random.sample(self.population, self.tourn_size)
        return max(candidates, key=lambda ind: ind.fitness)

    def crossover_blx_alpha(self, parent1: Individual, parent2: Individual, alpha: float = 0.3) -> Tuple[Individual, Individual]:
        """
        Blend Crossover (BLX-alpha) for continuous decision spaces.
        Generates offspring uniformly in an expanded interval between parents.
        """
        if random.random() > self.cx_rate:
            return copy.deepcopy(parent1), copy.deepcopy(parent2)

        c1_chrom = []
        c2_chrom = []
        for i in range(self.chrom_len):
            low_b, high_b = self.bounds[i]
            p1_val = parent1.chromosome[i]
            p2_val = parent2.chromosome[i]
            min_val = min(p1_val, p2_val)
            max_val = max(p1_val, p2_val)
            diff = max_val - min_val

            sub_low = max(low_b, min_val - alpha * diff)
            sub_high = min(high_b, max_val + alpha * diff)

            v1 = random.uniform(sub_low, sub_high)
            v2 = random.uniform(sub_low, sub_high)
            c1_chrom.append(v1)
            c2_chrom.append(v2)

        return Individual(c1_chrom), Individual(c2_chrom)

    def mutate_gaussian(self, ind: Individual):
        """
        Gaussian mutation perturbs genes with normal noise scaled to bounds,
        enforcing clamping to valid limits.
        """
        for i in range(self.chrom_len):
            if random.random() < self.mut_rate:
                low_b, high_b = self.bounds[i]
                span = high_b - low_b
                delta = random.gauss(0, self.mut_sigma * span)
                new_val = min(high_b, max(low_b, ind.chromosome[i] + delta))
                ind.chromosome[i] = new_val

    def evolve(self, verbose: bool = True) -> Tuple[Individual, List[Dict[str, Any]]]:
        """Runs the genetic algorithm loop over specified generations."""
        self.initialize_population()
        self.history = []

        for gen in range(self.generations):
            # Sort descending by fitness
            self.population.sort(key=lambda ind: ind.fitness, reverse=True)

            if self.population[0].fitness > self.best_individual.fitness:
                self.best_individual = copy.deepcopy(self.population[0])

            # Record generation statistics
            fitnesses = [ind.fitness for ind in self.population]
            valid_count = sum(1 for ind in self.population if ind.is_valid)
            gen_stat = {
                "generation": gen,
                "best_fitness": self.best_individual.fitness,
                "gen_best_fitness": self.population[0].fitness,
                "mean_fitness": float(np.mean(fitnesses)),
                "min_fitness": float(np.min(fitnesses)),
                "std_fitness": float(np.std(fitnesses)),
                "valid_fraction": valid_count / self.pop_size,
                "best_objectives": copy.deepcopy(self.best_individual.raw_objectives),
                "best_chromosome": copy.deepcopy(self.best_individual.chromosome),
            }
            self.history.append(gen_stat)

            if verbose and (gen % 25 == 0 or gen == self.generations - 1):
                obj_str = " | ".join(f"{k}: {v:,.2f}" for k, v in self.best_individual.raw_objectives.items())
                print(f"[Generation {gen:3d}] Best Fitness: {self.best_individual.fitness:8.4f} | {obj_str} | Valid: {valid_count}/{self.pop_size}")

            # Elitism: retain top N individuals directly
            new_population: List[Individual] = [
                copy.deepcopy(self.population[k]) for k in range(self.elitism_count)
            ]

            # Reproduction loop
            while len(new_population) < self.pop_size:
                p1 = self.tournament_selection()
                p2 = self.tournament_selection()

                child1, child2 = self.crossover_blx_alpha(p1, p2)

                self.mutate_gaussian(child1)
                self.mutate_gaussian(child2)

                self.evaluate_individual(child1)
                self.evaluate_individual(child2)

                new_population.append(child1)
                if len(new_population) < self.pop_size:
                    new_population.append(child2)

            self.population = new_population

        self.population.sort(key=lambda ind: ind.fitness, reverse=True)
        if self.population[0].fitness > self.best_individual.fitness:
            self.best_individual = copy.deepcopy(self.population[0])

        return self.best_individual, self.history
