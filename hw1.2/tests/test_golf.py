from unittest import TestCase

from golf.golf import Player, HitsMatch, HolesMatch


class HitsMatchTestCase(TestCase):
    def test_scenario(self):
        players = [Player('A'), Player('B'), Player('C')]
        m = HitsMatch(3, players)

        self._first_hole(m)
        self._second_hole(m)

        with self.assertRaises(RuntimeError):
            m.get_winners()

        self._third_hole(m)

        with self.assertRaises(RuntimeError):
            m.hit()

        self.assertEqual(m.get_winners(), [
            players[0], players[2]
        ])

    def _first_hole(self, m):
        m.hit()       # 1
        m.hit()       # 2
        m.hit(True)   # 3
        m.hit(True)   # 1
        for _ in range(8):
            m.hit()  # 2

        self.assertFalse(m.finished)
        self.assertEqual(m.get_table(), [
            ('A', 'B', 'C'),
            (2, 10, 1),
            (None, None, None),
            (None, None, None),
        ])

    def _second_hole(self, m):
        m.hit()  # 2
        for _ in range(3):
            m.hit(True)  # 3, 1, 2

        self.assertFalse(m.finished)
        self.assertEqual(m.get_table(), [
            ('A', 'B', 'C'),
            (2, 10, 1),
            (1, 2, 1),
            (None, None, None),
        ])

    def _third_hole(self, m):
        m.hit()      # 3
        m.hit(True)  # 1
        m.hit()      # 2
        self.assertEqual(m.get_table(), [
            ('A', 'B', 'C'),
            (2, 10, 1),
            (1, 2, 1),
            (1, None, None),
        ])
        m.hit(True)  # 3
        m.hit()      # 2
        m.hit(True)  # 2

        self.assertTrue(m.finished)
        self.assertEqual(m.get_table(), [
            ('A', 'B', 'C'),
            (2, 10, 1),
            (1, 2, 1),
            (1, 3, 2),
        ])

    def test_one_player_win(self):
        players = [Player('A'), Player('B'), Player('C')]
        match = HitsMatch(1, players)
        match.hit()  # A
        match.hit(True)  # B
        match.hit()  # C
        match.hit(True)  # A
        match.hit(True)  # C
        self.assertTrue(match.finished)
        self.assertEqual(match.get_table(), [
            ('A', 'B', 'C'),
            (2, 1, 2),
        ])
        self.assertEqual(match.get_winners(), [players[1]])

    def test_two_players_win(self):
        players = [Player('A'), Player('B'), Player("C")]
        match = HitsMatch(1, players)
        match.hit()  # A
        match.hit(True)  # B
        match.hit(True)  # C
        match.hit(True)  # A
        self.assertTrue(match.finished)
        self.assertEqual(match.get_table(), [
            ('A', 'B', 'C'),
            (2, 1, 1),
        ])
        self.assertEqual(match.get_winners(), [players[1], players[2]])

    def test_player_get_ten_unsuccessful_hits_in_one_hole(self):
        players = [Player('A'), Player('B')]
        match = HitsMatch(1, players)
        match.hit(True)  # A
        for _ in range(10):
            match.hit()  # B
        self.assertTrue(match.finished)
        self.assertEqual(match.get_table(), [
            ('A', 'B'),
            (1, 10),
        ])
        self.assertEqual(match.get_winners(), [players[0]])

    def test_table_contains_value_only_after_successful_hit(self):
        players = [Player('A'), Player('B')]
        match = HitsMatch(1, players)
        match.hit()  # A
        match.hit(True)  # B
        self.assertFalse(match.finished)
        self.assertEqual(match.get_table(), [
            ('A', 'B'),
            (None, 1)
        ])

    def test_hit_after_finish(self):
        players = [Player('A'), Player('B')]
        match = HitsMatch(1, players)
        match.hit(True)  # A
        match.hit(True)  # B
        with self.assertRaises(RuntimeError):
            match.hit()

    def test_get_winners_before_finish(self):
        players = [Player('A'), Player('B')]
        match = HitsMatch(1, players)
        match.hit()
        with self.assertRaises(RuntimeError):
            match.get_winners()


class HolesMatchTestCase(TestCase):
    def test_scenario(self):
        players = [Player('A'), Player('B'), Player('C')]
        m = HolesMatch(3, players)

        self._first_hole(m)
        self._second_hole(m)

        with self.assertRaises(RuntimeError):
            m.get_winners()

        self._third_hole(m)

        with self.assertRaises(RuntimeError):
            m.hit()

        self.assertEqual(m.get_winners(), [players[0]])

    def _first_hole(self, m):
        m.hit(True)  # 1
        m.hit()      # 2
        m.hit()      # 3

        self.assertFalse(m.finished)
        self.assertEqual(m.get_table(), [
            ('A', 'B', 'C'),
            (1, 0, 0),
            (None, None, None),
            (None, None, None),
        ])

    def _second_hole(self, m):
        for _ in range(10):
            for _ in range(3):
                m.hit()  # 2, 3, 1

        self.assertFalse(m.finished)
        self.assertEqual(m.get_table(), [
            ('A', 'B', 'C'),
            (1, 0, 0),
            (0, 0, 0),
            (None, None, None),
        ])

    def _third_hole(self, m):
        for _ in range(9):
            for _ in range(3):
                m.hit()  # 3, 1, 2
        m.hit(True)  # 3
        self.assertEqual(m.get_table(), [
            ('A', 'B', 'C'),
            (1, 0, 0),
            (0, 0, 0),
            (None, None, 1),
        ])
        m.hit(True)  # 1
        m.hit()      # 2

        self.assertTrue(m.finished)
        self.assertEqual(m.get_table(), [
            ('A', 'B', 'C'),
            (1, 0, 0),
            (0, 0, 0),
            (1, 0, 1),
        ])
