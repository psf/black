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
