from src.datageneration import make_files
from src.scoring import analyze, combos
from src.heatmap import heatmap
import sys
import os

# Get the folder where this script lives (project root)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Define paths relative to the project root
PATH_DATA = os.path.join(PROJECT_ROOT, "data")
PATH_OUTPUT = os.path.join(PROJECT_ROOT, "outputs")
HEATMAP_FOLDER = os.path.join(PROJECT_ROOT, "figures")


import sys

def augment(PATH_DATA: str, PATH_OUTPUT: str):
    """
    Handles user interaction and deck generation / analysis pipeline.
    """
    print("Welcome to the Penney Game Deck Generator!\n")

    response = input("Do you wish to augment the data set? (yes/no): ").strip().lower()

    if response in {"yes", "y"}:
        while True:
            try:
                tot_decks = int(input("How many decks would you like to generate?: ").strip())
                if tot_decks <= 0:
                    print("Please enter a positive number.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a number.")

        # Call generator
        print(f"\nGenerating {tot_decks} decks...")
        filepaths, file_sizes = make_files(tot_n=tot_decks, PATH_DATA=PATH_DATA)

        print(f"\n Done generating {len(filepaths)} file(s)!")
        for fp, size in zip(filepaths, file_sizes):
            print(f"Saved: {fp} ({size / 1_000_000:.2f} MB)")

        # Call analyzer
        print(f"\nAnalyzing decks...")
        analyze(data_folder=PATH_DATA, df_folder=PATH_OUTPUT, combos=combos, tot_decks = tot_decks)

        #Call figure maker
        print(f"\nCreating heatmaps...")
        heatmap(df_folder = PATH_OUTPUT, heatmap_folder = HEATMAP_FOLDER)
        print(f"Heatmaps saved to {HEATMAP_FOLDER}")
        print("\n All Done! Yippee!")
        sys.exit(0)

    elif response in {"no", "n"}:
        print(f"\nCreating heatmaps!")
        print(f"Heatmaps saved to {HEATMAP_FOLDER}")
        sys.exit(0) 

    else:
        print("Invalid response. Please run the program again and type 'yes' or 'no'.")
        sys.exit(1)


def main():
    """
    Main entry point — just calls augment()
    """

    augment(PATH_DATA, PATH_OUTPUT)


if __name__ == "__main__":
    main()
