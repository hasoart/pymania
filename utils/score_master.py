from typing import Tuple


class ScoreMaster:
    """
    Класс для удобной работы с очками, их подсчета и хранения.
    """

    def __init__(self):
        self.score_list = []
        self.score = 0
        self.combo = 0
        self.max_combo = 0

    def append(self, x: int) -> None:
        """
        Добавляет новые очки в список очков

        :param x: То, что добавляется в список. Допустимые значения - (300, 100, 50, 0, -1)
        :return: None
        """
        if x not in (-1, 0, 50, 100, 300):
            raise ValueError("Trying to append invalid value")

        if x >= 50:
            self.combo += 1
            self.score += x * self.combo
        else:
            self.combo = 0
        self.max_combo = max(self.combo, self.max_combo)
        self.score_list.append(x)

    def get_combo(self) -> int:
        """
        Возвращает текущее комбо
        :return: int
        """
        return self.combo

    def get_max_combo(self) -> int:
        """
        Возвращает максимальное комбо
        :return: int
        """
        return self.max_combo

    def get_score(self) -> int:
        """
        Возвращает текущие очки
        :return: int
        """
        return self.score

    def get_accuracy(self) -> float:
        """
        Возвращает текущую точность
        :return: float
        """
        return 100 * (sum(self.score_list) / (300 * len(self.score_list)) if self.score_list else 1.)

    def get_hit_counts(self) -> Tuple[int, int, int, int]:
        """
        Возвращает количество 300, 100, 50 и миссов

        :return: Количество 300, 100, 50 и миссов в виде (300, 100, 50, miss)
        """
        counts = [0, 0, 0, 0]

        for hit in self.score_list:
            if hit == 300:
                counts[0] += 1
            elif hit == 100:
                counts[1] += 1
            elif hit == 50:
                counts[2] += 1
            elif hit == 0:
                counts[3] += 1
            else:
                raise ValueError(f"Invalid value in score list: {hit}")

        return tuple(counts)

    def get_rank(self) -> str:
        """
        Calculates the rank of player's result due to accuracy and having misses.

        :return: Rank of the score - 'SS' if accuracy is 100%,
                                     'S' if accuracy is greater than 93.333% and there are no misses,
                                     'A' if accuracy is greater than 93.333% but there are misses,
                                     'B' if accuracy is greater than 85%,
                                     'C' if accuracy is greater than 75%,
                                     'D' if accuracy is lower than 75%
        """
        accuracy = self.get_accuracy()
        have_misses = bool(self.get_hit_counts()[3])

        if accuracy == 100:
            rank = 'SS'
        elif accuracy >= 93.333:
            if not have_misses:
                rank = 'S'
            else:
                rank = 'A'
        elif accuracy >= 85:
            rank = 'B'
        elif accuracy >= 75:
            rank = 'C'
        else:
            rank = 'D'

        return rank
