class C:

    def test(self) -> None:
        with patch("black.out", print):
            self.assertEqual(
                unstyle(str(report)), "1 file reformatted, 1 file failed to reformat."
            )
            self.assertEqual(
                unstyle(str(report)),
                "1 file reformatted, 1 file left unchanged, 1 file failed to reformat.",
            )
            self.assertEqual(
                unstyle(str(report)),
                "2 files reformatted, 1 file left unchanged, "
                "1 file failed to reformat.",
            )
            self.assertEqual(
                unstyle(str(report)),
                "2 files reformatted, 2 files left unchanged, "
                "2 files failed to reformat.",
            )
            for i in (a,):
                if (
                    # Rule 1
                    i % 2 == 0
                    # Rule 2
                    and i % 3 == 0
                ):
                    while (
                        # Just a comment
                        call()
                        # Another
                    ):
                        print(i)

    def omitting_trailers() -> None:
        get_collection(
            hey_this_is_a_very_long_call, it_has_funny_attributes, really=True
        )[OneLevelIndex]
        get_collection(
            hey_this_is_a_very_long_call, it_has_funny_attributes, really=True
        )[OneLevelIndex][TwoLevelIndex][ThreeLevelIndex][FourLevelIndex]
        d[0][1][2][3][4][5][6][7][8][9][10][11][12][13][14][15][16][17][18][19][20][21][
            22
        ]
