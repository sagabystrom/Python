#!/usr/bin/env python3

import typingtest

def main():

    filename = ""

    stop = False
    while not stop:

        print("===Speed typing test===")
        print("1. Easy mode")
        print("2. Medium mode")
        print("3. Hard mode")
        print("4. Show high score")
        print("q. Quit")

        choice = input("")
        if choice in ["1", "2", "3"]:
            if choice == "1":
                filename = "texts/easy.txt"
            elif choice == "2":
                filename = "texts/medium.txt"
            else:
                filename = "texts/hard.txt"
            typingtest.run_typing_test(filename)

        elif choice == "4":
            typingtest.read_and_print_scores("scores.txt")

        elif choice == "q":
            print("Bye!")
            stop = True

        else:
            print("Not a valid choice")

        if not stop:
            input("\nPress Enter to go back to the menu")
            print("\n")

if __name__ == "__main__":
    main()
