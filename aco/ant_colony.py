import numpy as np
from typing import List, Set, Tuple

class AntColony:
    """
    Karınca Koloni Optimizasyonu (ACO) algoritması.

    Attributes:
        distance_matrix (np.ndarray): NxN mesafe matrisi.
        n_ants (int): Tur başına karınca sayısı.
        n_iterations (int): İterasyon sayısı.
        alpha (float): Feromon etkisi katsayısı.
        beta (float): Görünürlük etkisi katsayısı.
        evaporation_rate (float): Feromon buharlaşma oranı.
        q (float): Feromon ekleme sabiti.
    """

    def __init__(
        self,
        distance_matrix: np.ndarray,
        n_ants: int = 10,
        n_iterations: int = 50,
        alpha: float = 1.0,
        beta: float = 2.0,
        evaporation_rate: float = 0.5,
        q: float = 100.0,
    ) -> None:
        """
        Args:
            distance_matrix: Şehirler arası mesafe matrisi (NxN).
            n_ants: Her iterasyonda gezdireceğimiz karınca sayısı.
            n_iterations: Toplam iterasyon sayısı.
            alpha: Feromon gücünün olasılığa etkisi.
            beta: Görünürlük (1/mesafe) etkisinin olasılığa etkisi.
            evaporation_rate: Her iterasyonda feromon buharlaşma oranı.
            q: Feromon bırakma sabiti.
        """
        self.distance_matrix: np.ndarray = distance_matrix
        self.n_cities: int = distance_matrix.shape[0]
        self.n_ants: int = n_ants
        self.n_iterations: int = n_iterations
        self.alpha: float = alpha
        self.beta: float = beta
        self.evaporation_rate: float = evaporation_rate
        self.q: float = q

        # Başlangıçta tüm kenarlara eşit feromon
        self.pheromone_matrix: np.ndarray = np.ones((self.n_cities, self.n_cities))

        self.best_route: List[int] = []
        self.best_distance: float = float('inf')

    def run(self) -> Tuple[List[int], float]:
        """
        Ana döngü: Karıncalar rota oluşturur, en iyi rota güncellenir,
        feromonlar güncellenir.

        Returns:
            Tuple[best_route, best_distance]
        """
        for _ in range(self.n_iterations):
            routes: List[List[int]] = []
            distances: List[float] = []

            for _ in range(self.n_ants):
                route: List[int] = self.construct_route()
                distance: float = self.calculate_route_distance(route)
                routes.append(route)
                distances.append(distance)

                if distance < self.best_distance:
                    self.best_distance = distance
                    self.best_route = route

            self.update_pheromones(routes, distances)

        return self.best_route, self.best_distance

    def construct_route(self) -> List[int]:
        """
        Rastgele başlangıç şehrinden başlayıp tüm şehirleri
        ziyaret eden bir rota oluşturur.
        """
        route: List[int] = []
        visited: Set[int] = set()

        current_city: int = np.random.randint(self.n_cities)
        route.append(current_city)
        visited.add(current_city)

        while len(visited) < self.n_cities:
            next_city: int = self.select_next_city(current_city, visited)
            route.append(next_city)
            visited.add(next_city)
            current_city = next_city

        return route

    def select_next_city(self, current_city: int, visited: Set[int]) -> int:
        """
        Olasılıksal seçim:
        P(i->j) ~ [pheromone(i,j)^alpha] * [visibility(i,j)^beta]
        """
        probabilities: np.ndarray = np.zeros(self.n_cities)

        for city in range(self.n_cities):
            if city not in visited:
                pheromone: float = self.pheromone_matrix[current_city, city] ** self.alpha
                distance: float = self.distance_matrix[current_city, city] or 1e-10
                visibility: float = (1.0 / distance) ** self.beta
                probabilities[city] = pheromone * visibility

        total = probabilities.sum()
        if total == 0:
            choices = [c for c in range(self.n_cities) if c not in visited]
            return int(np.random.choice(choices))

        probabilities /= total
        return int(np.random.choice(range(self.n_cities), p=probabilities))

    def calculate_route_distance(self, route: List[int]) -> float:
        """
        Verilen rotanın toplam mesafesini hesaplar (başlangıca dönüş dahil).
        """
        distance: float = 0.0
        for i in range(len(route) - 1):
            distance += self.distance_matrix[route[i], route[i+1]]
        distance += self.distance_matrix[route[-1], route[0]]
        return distance

    def update_pheromones(self, routes: List[List[int]], distances: List[float]) -> None:
        """
        Feromon buharlaşması ve karıncaların bıraktığı feromonu günceller.
        """
        # Buharlaşma
        self.pheromone_matrix *= (1 - self.evaporation_rate)

        # Rota bazlı feromon ekleme
        for route, dist in zip(routes, distances):
            deposit: float = self.q / dist
            for i in range(len(route) - 1):
                a, b = route[i], route[i+1]
                self.pheromone_matrix[a, b] += deposit
                self.pheromone_matrix[b, a] += deposit

            # Son noktadan başlangıca dönüş
            a, b = route[-1], route[0]
            self.pheromone_matrix[a, b] += deposit
            self.pheromone_matrix[b, a] += deposit
