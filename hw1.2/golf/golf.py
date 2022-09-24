import itertools


class Player:
    def __init__(self, name):
        self.name = name


class Match:
    def __init__(self, countHoles, players):
        self.countHoles = countHoles
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

    def init_table(self):
        table = [tuple(player.name for player in self.players)]
        for _ in range(self.countHoles):
            table.append([None for _ in self.players])
        return table

    def hit(self, success=False):
        pass

    def get_winners(self):
        if self.finished:
            result = {player: 0 for player in self.players}
            for i in range(1, self.countHoles+1):
                for player in self.players:
                    player_number = self.players_numbers[player.name]
                    result[player] += self.table[i][player_number]
            winner_score = min(result.values())
            winners = [
                player for player in result
                if result[player] == winner_score
            ]
            return winners
        raise RuntimeError("Матч не закончился, нельзя определить победителя")

    def get_table(self):
        # не очень понимаю, зачем в тестах было требование о том,
        # что результат по каждой лунке должен быть tuple,
        # из-за этого написала такую штуку вместо return self.table
        result = []
        for row in self.table:
            result.append(tuple(row))
        return result

    def update_table(self, player_number, player_result, hole_number):
        self.table[hole_number][player_number] = player_result


class HitsMatch(Match):
    def __init__(self, countHoles, players):
        super().__init__(countHoles, players)
        self.max_hits_count = 10

    def hit(self, success=False):
        if self.finished:
            raise RuntimeError("Матч закончился, игрок не может делать удар")
        if self.changed_player:
            self.current_player = self.players_iterator.__next__().name
        player_number = self.players_numbers[self.current_player]
        if self.is_all_players_get_score(self.current_hole):
            self.change_hole()
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

    def is_all_players_get_score(self, current_hole):
        return None not in self.table[current_hole]

    def is_player_wins_hole(self, current_hole, current_player):
        return self.table[current_hole][current_player] is not None

    def change_hole(self):
        if self.current_hole == self.countHoles:
            self.finished = True
            return
        self.current_count_hits = {
            player.name: 0 for player in self.players
        }
        self.changed_player = True
        self.current_hole += 1


class HolesMatch(Match):
    pass
