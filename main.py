# from src.datageneration import make_files
# from src.scoring import analyze, combos
# from src.heatmap import heatmap



# make_files(tot_n = 9, max_decks= 2)

# analyze(data_folder= "C:/Users/kmand/DATA 440/Penney-Game/data", df_folder = "C:/Users/kmand/DATA 440/Penney-Game/outputs", df_name = 'scoring_analysis', combos = combos)

# heatmap(path = "C:/Users/kmand/DATA 440/Penney-Game/outputs")

from src.datageneration import make_files
from src.scoring import analyze, combos
from src.heatmap import heatmap
import sys

PATH_DATA = "/Users/lexnguyen/Library/CloudStorage/OneDrive-William&Mary/Fall 2025/DATA_440/Penney-Game/data"
PATH_OUTPUT = "/Users/lexnguyen/Library/CloudStorage/OneDrive-William&Mary/Fall 2025/DATA_440/Penney-Game/outputs"
HEATMAP_FOLDER = "/Users/lexnguyen/Library/CloudStorage/OneDrive-William&Mary/Fall 2025/DATA_440/Penney-Game/figures"



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
