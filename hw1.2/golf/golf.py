import itertools
from typing import List, Tuple


class Player:
    def __init__(self, name: str):
        self.name = name


class Match:
    def __init__(self, count_holes: int, players: List[Player]):
        self.countHoles = count_holes
        self.players = players
        self.finished = False
        self.changed_player = True
        self.current_player = None
        self.current_hole = 1
        self.table = self.init_table()
        self.players_iterator = itertools.cycle(players)
        self.current_count_hits = {player.name: 0 for player in self.players}
        self.players_numbers = {
            player.name: number for number, player in enumerate(self.players)
        }

    def init_table(self) -> List[List]:
        table = [[player.name for player in self.players]]
        for _ in range(self.countHoles):
            table.append([None for _ in self.players])
        return table

    def hit(self, success=False) -> bool:
        pass

    def get_winners(self, is_max_score=False) -> List[Player]:
        if self.finished:
            result = {player: 0 for player in self.players}
            for i in range(1, self.countHoles+1):
                for player in self.players:
                    player_number = self.players_numbers[player.name]
                    result[player] += self.table[i][player_number]
            if is_max_score:
                winner_score = max(result.values())
            else:
                winner_score = min(result.values())
            winners = [
                player for player in result
                if result[player] == winner_score
            ]
            return winners
        raise RuntimeError("Матч не закончился, нельзя определить победителя")

    def get_table(self) -> List[Tuple]:
        # не очень понимаю, зачем в тестах было требование о том,
        # что результат по каждой лунке должен быть tuple,
        # из-за этого написала такую штуку вместо return self.table
        result = []
        for row in self.table:
            result.append(tuple(row))
        return result

    def update_table(self, player_number: int, player_result: int, hole_number: int):
        self.table[hole_number][player_number] = player_result


class HitsMatch(Match):
    def __init__(self, count_holes: int, players: List[Player]):
        super().__init__(count_holes, players)
        self.max_hits_count = 10

    def hit(self, success=False):
        if self.finished:
            raise RuntimeError("Матч закончился, игрок не может делать удар")
        if self.changed_player:
            self.current_player = self.players_iterator.__next__().name
        player_number = self.players_numbers[self.current_player]
        if self.is_all_players_get_score(self.current_hole) and not self.change_hole_is_successful():
            return
        if not self.is_player_wins_hole(self.current_hole, player_number):
            self.current_count_hits[self.current_player] += 1
            if success:
                self.update_table(
                    player_number,
                    self.current_count_hits[self.current_player],
                    self.current_hole
                )
                self.changed_player = True
                if self.current_hole == self.countHoles and \
                        self.is_all_players_get_score(self.current_hole):
                    self.finished = True
            else:
                if self.current_count_hits[self.current_player] == \
                        self.max_hits_count - 1:
                    self.update_table(
                        player_number,
                        self.max_hits_count,
                        self.current_hole
                    )
                    self.changed_player = False
        else:
            self.hit(success)

    def is_all_players_get_score(self, current_hole: int) -> bool:
        return None not in self.table[current_hole]

    def is_player_wins_hole(self, current_hole: int, current_player: int) -> bool:
        return self.table[current_hole][current_player] is not None

    def change_hole_is_successful(self) -> bool:
        if self.current_hole == self.countHoles:
            self.finished = True
            return False
        self.current_count_hits = {
            player.name: 0 for player in self.players
        }
        self.changed_player = True
        self.current_hole += 1
        return True

    def get_winners(self, is_max_score=False) -> List[Player]:
        return super().get_winners(is_max_score=is_max_score)


class HolesMatch(Match):
    def __init__(self, count_holes: int, players: List[Player]):
        super().__init__(count_holes, players)
        self.current_player = 0
        self.current_count_rounds = 0
        self.number_player = 0

    def hit(self, success=False):
        self.current_player %= len(self.players)
        self.number_player %= len(self.players)
        if self.finished:
            raise RuntimeError("Матч закончился, игрок не может делать удар")
        if success:
            self.table[self.current_hole][self.current_player] = 1
        if 1 in self.table[self.current_hole] and self.number_player == 2:
            current_hole_result = self.table[self.current_hole]
            self.table[self.current_hole] = list(map(
                lambda x: 0 if x is None else 1,
                current_hole_result
            ))
            self.current_player += 1
            self.current_hole += 1
            self.current_count_rounds = 0
            if self.current_hole > self.countHoles:
                self.finished = True
        elif self.current_count_rounds == 9 and self.number_player == 2:
            self.table[self.current_hole] = [0 for _ in self.players]
            self.current_count_rounds = 0
            self.current_hole += 1
            self.current_player += 1
            if self.current_hole > self.countHoles:
                self.finished = True
        elif self.number_player == 2:
            self.current_count_rounds += 1
        self.current_player += 1
        self.number_player += 1

    def get_winners(self, is_max_score=True) -> List[Player]:
        return super().get_winners(is_max_score=is_max_score)