from main import TvProgramBotErrorMessages, TvProgramBot


class TestBot:
    bot = TvProgramBot("token")

    def create_updates(self, t: str):
        return [{"update_id": 1, "message": {"chat": {"id": 0}, "text": t}}]

    def create_invalid_updates(self):
        return [{"update_id": 1, "message": {"chat": {"id": 0}}}]

    def test_search_existing_program_by_full_name(self):
        response = self.bot.process_updates(self.create_updates("friends"))
        expected_response = (
            "Name: Friends\n"
            "Network Name: NBC\n"
            "Network Country Name: United States\n"
            "Summary: <p>Six young (20-something) people from New York City "
            "(Manhattan), on their own and struggling to survive in the real "
            "world, find the companionship, comfort and support they get "
            "from each other to be the perfect antidote to the pressures "
            "of life.</p><p>This average group of buddies goes through "
            "massive mayhem, family trouble, past and future romances, "
            "fights, laughs, tears and surprises as they learn what it "
            "really means to be a friend.</p>"
        )
        assert response == expected_response

    def test_search_existing_program_by_part_name(self):
        response = self.bot.process_updates(self.create_updates("quee"))
        expected_response = (
            "Name: Queen Sugar\n"
            "Network Name: Oprah Winfrey Network\n"
            "Network Country Name: United States\n"
            "Summary: <p>The contemporary drama <b>Queen Sugar</b>, set in the"
            " fictional town of Saint Josephine, Louisiana, chronicles the "
            "lives and loves of the estranged Bordelon siblings: Nova, a "
            "worldly-wise journalist and activist; Charley, the savvy wife "
            "and manager of a professional basketball star; and Ralph Angel, "
            "a formerly incarcerated young father in search of redemption. "
            "After a family tragedy, the Bordelons must navigate the triumphs "
            "and struggles of their complicated lives in order to run a "
            "struggling sugarcane farm in the Deep South.</p>"
        )
        assert response == expected_response

    def test_search_without_full_info_program(self):
        response = self.bot.process_updates(self.create_updates("fr"))
        assert response == TvProgramBotErrorMessages.NO_FULL_INFO.value

    def test_search_nonexistent_program(self):
        response = self.bot.process_updates(self.create_updates("123456"))
        assert response == TvProgramBotErrorMessages.NOT_FOUND.value

    def test_get_incorrect_message(self):
        response = self.bot.process_updates(self.create_invalid_updates())
        assert response == TvProgramBotErrorMessages.NO_TEXT.value
