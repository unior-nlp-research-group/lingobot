# -*- coding: utf-8 -*-
import utility

if __name__ == "__main__":
    test_unindent = utility.unindent(
        """
        Let’s find the intruder! 🐸
        """
    )
    print(test_unindent)