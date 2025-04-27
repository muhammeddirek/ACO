import numpy as np

class AntColony:
    def __init__(self, distance_matrix, n_ants, n_iterations, alpha=1.0, beta=2.0, evaporation_rate=0.5, start_city=0):
        self.distance_matrix = distance_matrix
        self.n_ants = n_ants
        self.n_iterations = n_iterations
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        self.start_city = start_city
        self.n_cities = distance_matrix.shape[0]
        self.pheromone = np.ones(self.distance_matrix.shape) / self.n_cities

    def run(self):
        best_route = None
        best_distance = float('inf')

        for _ in range(self.n_iterations):
            all_routes = self.construct_routes()
            self.spread_pheromone(all_routes)
            current_best_route, current_best_distance = min(all_routes, key=lambda x: x[1])
            
            if current_best_distance < best_distance:
                best_route = current_best_route
                best_distance = current_best_distance

            self.pheromone *= (1 - self.evaporation_rate)

        return best_route, best_distance

    def construct_routes(self):
        routes = []

        for _ in range(self.n_ants):
            route = [self.start_city]
            visited = set(route)

            while len(route) < self.n_cities:
                current_city = route[-1]
                move_probs = self.calculate_move_probabilities(current_city, visited)
                if move_probs.sum() == 0:
                    break  # Eğer sıkışırsa (gidecek şehir kalmazsa) dur
                next_city = self.select_next_city(move_probs)
                route.append(next_city)
                visited.add(next_city)

            routes.append((route, self.calculate_total_distance(route)))

        return routes

    def calculate_move_probabilities(self, current_city, visited):
        pheromone = np.copy(self.pheromone[current_city])
        visibility = 1 / (self.distance_matrix[current_city] + 1e-10)

        no_connection = np.isinf(self.distance_matrix[current_city])
        pheromone[no_connection] = 0
        visibility[no_connection] = 0

        pheromone[list(visited)] = 0
        visibility[list(visited)] = 0

        numerator = (pheromone ** self.alpha) * (visibility ** self.beta)
        denominator = np.sum(numerator)

        if denominator == 0:
            return np.zeros(self.n_cities)
        else:
            return numerator / denominator

    def select_next_city(self, probabilities):
        return np.random.choice(range(self.n_cities), p=probabilities)

    def spread_pheromone(self, all_routes):
        for route, distance in all_routes:
            for i in range(len(route) - 1):
                self.pheromone[route[i], route[i + 1]] += 1 / distance
                self.pheromone[route[i + 1], route[i]] += 1 / distance

    def calculate_total_distance(self, route):
        distance = 0
        for i in range(len(route) - 1):
            distance += self.distance_matrix[route[i], route[i + 1]]
        distance += self.distance_matrix[route[-1], route[0]]  # Başlangıç noktasına dönüş
        return distance
