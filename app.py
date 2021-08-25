from scripts import crafting, recipe


if __name__ == "__main__":
    while True:
        print("\n1. Run Crafter")
        print("2. Run Recipe Maker")
        print("Anything else to quit")
        choice = input("Choice: ")

        if choice == "1":
            crafting.run()
        elif choice == "2":
            recipe.run()
        else:
            break
