import numpy as np
from typing import List, Set, Tuple

class AntColony:
    def __init__(self, distance_matrix: np.ndarray, n_ants: int = 10, n_iterations: int = 50,
                 alpha: float = 1.0, beta: float = 2.0, evaporation_rate: float = 0.5, q: float = 100.0) -> None:
        self.distance_matrix = distance_matrix
        self.n_cities = distance_matrix.shape[0]
        self.n_ants = n_ants
        self.n_iterations = n_iterations
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        self.q = q

        self.pheromone_matrix = np.ones((self.n_cities, self.n_cities))
        self.best_route = []
        self.best_distance = float('inf')

    def run(self) -> Tuple[List[int], float]:
        for _ in range(self.n_iterations):
            routes, distances = [], []
            for _ in range(self.n_ants):
                route = self.construct_route()
                distance = self.calculate_route_distance(route)
                routes.append(route)
                distances.append(distance)
                if distance < self.best_distance:
                    self.best_distance = distance
                    self.best_route = route
            self.update_pheromones(routes, distances)
        return self.best_route, self.best_distance

    def construct_route(self) -> List[int]:
        route = []
        visited = set()
        current_city = np.random.randint(self.n_cities)
        route.append(current_city)
        visited.add(current_city)

        while len(visited) < self.n_cities:
            next_city = self.select_next_city(current_city, visited)
            route.append(next_city)
            visited.add(next_city)
            current_city = next_city

        return route

    def select_next_city(self, current_city: int, visited: Set[int]) -> int:
        probabilities = np.zeros(self.n_cities)
        for city in range(self.n_cities):
            if city not in visited:
                pheromone = self.pheromone_matrix[current_city, city] ** self.alpha
                distance = self.distance_matrix[current_city, city] or 1e-10
                visibility = (1.0 / distance) ** self.beta
                probabilities[city] = pheromone * visibility

        total = probabilities.sum()
        if total == 0:
            choices = [c for c in range(self.n_cities) if c not in visited]
            return int(np.random.choice(choices))
        probabilities /= total
        return int(np.random.choice(range(self.n_cities), p=probabilities))

    def calculate_route_distance(self, route: List[int]) -> float:
        distance = sum(self.distance_matrix[route[i], route[i+1]] for i in range(len(route)-1))
        distance += self.distance_matrix[route[-1], route[0]]
        return distance

    def update_pheromones(self, routes: List[List[int]], distances: List[float]) -> None:
        self.pheromone_matrix *= (1 - self.evaporation_rate)
        for route, dist in zip(routes, distances):
            deposit = self.q / dist
            for i in range(len(route)-1):
                a, b = route[i], route[i+1]
                self.pheromone_matrix[a, b] += deposit
                self.pheromone_matrix[b, a] += deposit
            a, b = route[-1], route[0]
            self.pheromone_matrix[a, b] += deposit
            self.pheromone_matrix[b, a] += deposit
