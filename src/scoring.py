import pandas as pd
import numpy as np
import os
import re

def load_first_raw_file(path: str) -> tuple[np.ndarray, str]:
    """
    Load the first file in a folder whose name contains 'raw' using np.load.
    
    Parameters:
        path (str): Folder path to search for files.
        
    Returns:
        tuple[np.ndarray, str]: Loaded NumPy array and the filename.
                                Returns (None, None) if no file found.
    """
    # List all files in the folder
    all_files = os.listdir(path)

    # Filter only files with "raw" in the name
    raw_files = [f for f in all_files if "raw" in f and os.path.isfile(os.path.join(path, f))]

    if not raw_files:
        print("No raw files found in the folder.")
        return None, None

    # Sort for consistency and pick the first one
    raw_files.sort()
    first_file_name = raw_files[0]
    full_path = os.path.join(path, first_file_name)
    print(f"Loading file: {full_path}")

    # Load the file
    array = np.load(full_path)
    
    return array, first_file_name
    
def count_raw_files(path: str) -> int:
    """
    Count the number of files in the given folder whose filename contains 'raw'.

    Parameters:
        path (str): Folder path to search.

    Returns:
        int: Number of files with 'raw' in the filename.
    """
    count = 0
    for fname in os.listdir(path):
        full_path = os.path.join(path, fname)
        if os.path.isfile(full_path) and "raw" in fname:
            count += 1

    return count



# once read, change name
def rename_raw_to_cooked(path: str, filename: str) -> str:
    """
    Rename a single file starting with 'raw-deck' to 'cooked-deck'.

    Parameters:
        path (str): folder path
        filename (str): name of the file to rename

    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the filename does not start with 'raw-deck'

    Returns:
        str: The new filename
    """
    old_path = os.path.join(path, filename)

    # Check if file exists
    if not os.path.isfile(old_path):
        raise FileNotFoundError(f"File not found: {old_path}")

    # Check if filename starts with 'raw-deck'
    if not filename.startswith("raw-deck"):
        raise ValueError(f"Filename does not start with 'raw-deck': {filename}")

    # Build new filename and path
    new_name = filename.replace("raw-deck", "cooked-deck", 1)
    new_path = os.path.join(path, new_name)

    # Rename the file
    os.rename(old_path, new_path)

    return new_name

def check_or_create_wins_df(folder: str, combos: list[dict]) -> pd.DataFrame:
    base_filename = "scoring_analysis"
    pattern = re.compile(rf"{base_filename}_N=\d+\.csv")
    
    found_file = None
    for f in os.listdir(folder):
        if pattern.match(f):
            found_file = f
            break
    
    if found_file:
        filepath = os.path.join(folder, found_file)
        print(f"Found existing file: {filepath}. Loading DataFrame.")
        df = pd.read_csv(filepath, dtype={"p1": str, "p2": str})
    
        n_match = re.search(r"_N=(\d+)", found_file)
        decks_scored = int(n_match.group(1)) if n_match else 0
    else:
        print(f"No existing file found. Creating blank DataFrame with {len(combos)} rows.")
        df = pd.DataFrame(combos)
        df.rename(columns={"player_a": "p1", "player_b": "p2"}, inplace=True)
        
        # Ensure p1 and p2 are strings
        df["p1"] = df["p1"].astype(str)
        df["p2"] = df["p2"].astype(str)
        
        # Add scoring columns
        for col in ["p1_wins_cards", "p1_wins_tricks", "p2_wins_cards", 
                    "p2_wins_tricks", "draws_cards", "draws_tricks"]:
            df[col] = 0
        
        decks_scored = 0
        
    return df, decks_scored

def score_deck(deck: np.ndarray, combos: list) -> pd.DataFrame:
    """
    Scores a single deck for both trick and card scoring.

    Parameters:
        deck (np.ndarray): the deck to score
        combos (list): a list of all the combinations of players' choices
                       each combo is a dict: {"player_a": tuple, "player_b": tuple}
    
    Returns:
        pd.DataFrame: deck number, player combos, and scores
    """
    rows = []

    # Ensure deck is string format
    deck_str = ''.join(['1' if card else '0' for card in deck])


    for combo in combos:
        p1 = str(combo["player_a"])
        p2 = str(combo["player_b"])

        p1_tricks = 0
        p1_cards = 0
        p2_tricks = 0
        p2_cards = 0

        i = 0  # starting position in deck_str
        cards_to_win = 3

        while i <= len(deck_str) - 3:
            window = deck_str[i:i+3]

            if window == p1:
                p1_tricks += 1
                p1_cards += cards_to_win
                i += 3  # skip next 3 cards
                cards_to_win = 3
            elif window == p2:
                p2_tricks += 1
                p2_cards += cards_to_win
                i += 3  # skip next 3 cards
                cards_to_win = 3
            else:
                i += 1  # move window by 1
                cards_to_win += 1

        rows.append({
            "Decks": list(deck_str),
            "p1": p1,
            "p2": p2,
            "p1_tricks": p1_tricks,
            "p1_cards": p1_cards,
            "p2_tricks": p2_tricks,
            "p2_cards": p2_cards
        })

    df = pd.DataFrame(rows)
    return df
    
def save_dataframe_to_csv(df: pd.DataFrame, folder: str, num_of_decks_scored: int) -> None:
    """
    Safely save DataFrame as 'scoring_analysis_N=###.csv'.
    Keeps the previous file until the new one is fully written.
    """
    base_filename = "scoring_analysis"
    
    os.makedirs(folder, exist_ok=True)
    new_filename = f"{base_filename}_N={num_of_decks_scored}.csv"
    temp_filename = f"{base_filename}_N={num_of_decks_scored}_temp.csv"
    new_filepath = os.path.join(folder, new_filename)
    temp_filepath = os.path.join(folder, temp_filename)

    # Step 1: Write to temp file
    df.to_csv(temp_filepath, index=False)

    # Step 2: Remove older completed files (but not the new temp)
    for f in os.listdir(folder):
        if re.match(rf"{re.escape(base_filename)}_N=\d+\.csv$", f) and f != new_filename:
            os.remove(os.path.join(folder, f))

    # Step 3: Rename temp → final
    os.rename(temp_filepath, new_filepath)

    print(f"Safely saved: {new_filepath}")

def count_wins(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a DataFrame with results from a single deck, compute win/loss/draw counts 
    for both game modes (tricks and cards).
    
    Input format:
    Decks | p1 | p2 | p1_tricks | p1_cards | p2_tricks | p2_cards
    
    Output format:
    p1 | p2 | p1_wins_tricks | p2_wins_tricks | draws_tricks |
              p1_wins_cards | p2_wins_cards | draws_cards
    """
    
    results = []

    for _, row in df.iterrows():
        p1, p2 = row["p1"], row["p2"]

        # Initialize counters for one row
        p1_wins_tricks = p2_wins_tricks = draws_tricks = 0
        p1_wins_cards  = p2_wins_cards  = draws_cards  = 0

        # Tricks comparison
        if row["p1_tricks"] > row["p2_tricks"]:
            p1_wins_tricks = 1
        elif row["p1_tricks"] < row["p2_tricks"]:
            p2_wins_tricks = 1
        else:
            draws_tricks = 1

        # Cards comparison
        if row["p1_cards"] > row["p2_cards"]:
            p1_wins_cards = 1
        elif row["p1_cards"] < row["p2_cards"]:
            p2_wins_cards = 1
        else:
            draws_cards = 1

        results.append({
            "p1": p1,
            "p2": p2,
            "p1_wins_tricks": p1_wins_tricks,
            "p2_wins_tricks": p2_wins_tricks,
            "draws_tricks": draws_tricks,
            "p1_wins_cards": p1_wins_cards,
            "p2_wins_cards": p2_wins_cards,
            "draws_cards": draws_cards,
        })

    return pd.DataFrame(results)

def update_results(results_df: pd.DataFrame, scores_df: pd.DataFrame) -> pd.DataFrame:
    # Force identifier columns to be strings
    for col in ["p1", "p2"]:
        results_df[col] = results_df[col].astype(str)
        scores_df[col] = scores_df[col].astype(str)
    
    # Merge on p1 and p2
    merged = results_df.merge(
        scores_df,
        on=["p1", "p2"],
        how="left",
        suffixes=("", "_new")
    )

    score_columns = [
        "p1_wins_tricks", "p2_wins_tricks", "draws_tricks",
        "p1_wins_cards", "p2_wins_cards", "draws_cards"
    ]

    for col in score_columns:
        new_col = col + "_new"
        if new_col in merged:
            merged[col] = pd.to_numeric(merged[col], errors="coerce").fillna(0)
            merged[new_col] = pd.to_numeric(merged[new_col], errors="coerce").fillna(0)
            merged[col] = merged[col] + merged[new_col]
            merged = merged.drop(columns=new_col)

    return merged

def analyze(data_folder: str, df_folder: str, combos: list, tot_decks: int):
    """
    Load all raw deck files, score each deck using combos, and save/update a cumulative DataFrame.
    Prints cumulative progress over total number of decks.
    """

    # Load or create cumulative DataFrame
    df, num_of_decks_scored = check_or_create_wins_df(df_folder, combos)

    # Get all raw files
    raw_files = sorted([f for f in os.listdir(data_folder) if "raw" in f and os.path.isfile(os.path.join(data_folder, f))])
    if not raw_files:
        print("No raw files found to process.")
        return


    total_decks = tot_decks
    total_decks_processed = 0

    # Process decks file by file
    for file_idx, filename in enumerate(raw_files):
        full_path = os.path.join(data_folder, filename)
        decks = np.load(full_path)
        if decks.ndim == 1:
            decks = decks[np.newaxis, :]
        elif decks.ndim == 3 and decks.shape[0] == 1:
            decks = decks[0]

        for single_deck in decks:
            df_scores = score_deck(single_deck, combos)
            df_wins = count_wins(df_scores)
            df = update_results(df, df_wins)

            total_decks_processed += 1
            num_of_decks_scored += 1

            # Update every 10k decks or at the last deck
            if (total_decks_processed % 10000 == 0) or (total_decks_processed == total_decks):
                progress_percent = (total_decks_processed / total_decks) * 100
                print(f"Processed {total_decks_processed}/{total_decks} decks ({progress_percent:.2f}%)", end='\r', flush=True)

        # Rename after processing
        rename_raw_to_cooked(data_folder, filename)
        
    save_dataframe_to_csv(df, df_folder, num_of_decks_scored)
    print(f"Total decks scored: {num_of_decks_scored}")
    

#list of dictionaries with the 56 relevant players' choices combos
combos = [
    {"player_a": '000', "player_b": '001'},
    {"player_a": '000', "player_b": '010'},
    {"player_a": '000', "player_b": '011'},
    {"player_a": '000', "player_b": '100'},
    {"player_a": '000', "player_b": '101'},
    {"player_a": '000', "player_b": '110'},
    {"player_a": '000', "player_b": '111'},
    {"player_a": '001', "player_b": '000'},
    {"player_a": '001', "player_b": '010'},
    {"player_a": '001', "player_b": '011'},
    {"player_a": '001', "player_b": '100'},
    {"player_a": '001', "player_b": '101'},
    {"player_a": '001', "player_b": '110'},
    {"player_a": '001', "player_b": '111'},
    {"player_a": '010', "player_b": '000'},
    {"player_a": '010', "player_b": '001'},
    {"player_a": '010', "player_b": '011'},
    {"player_a": '010', "player_b": '100'},
    {"player_a": '010', "player_b": '101'},
    {"player_a": '010', "player_b": '110'},
    {"player_a": '010', "player_b": '111'},
    {"player_a": '011', "player_b": '000'},
    {"player_a": '011', "player_b": '001'},
    {"player_a": '011', "player_b": '010'},
    {"player_a": '011', "player_b": '100'},
    {"player_a": '011', "player_b": '101'},
    {"player_a": '011', "player_b": '110'},
    {"player_a": '011', "player_b": '111'},
    {"player_a": '100', "player_b": '000'},
    {"player_a": '100', "player_b": '001'},
    {"player_a": '100', "player_b": '010'},
    {"player_a": '100', "player_b": '011'},
    {"player_a": '100', "player_b": '101'},
    {"player_a": '100', "player_b": '110'},
    {"player_a": '100', "player_b": '111'},
    {"player_a": '101', "player_b": '000'},
    {"player_a": '101', "player_b": '001'},
    {"player_a": '101', "player_b": '010'},
    {"player_a": '101', "player_b": '011'},
    {"player_a": '101', "player_b": '100'},
    {"player_a": '101', "player_b": '110'},
    {"player_a": '101', "player_b": '111'},
    {"player_a": '110', "player_b": '000'},
    {"player_a": '110', "player_b": '001'},
    {"player_a": '110', "player_b": '010'},
    {"player_a": '110', "player_b": '011'},
    {"player_a": '110', "player_b": '100'},
    {"player_a": '110', "player_b": '101'},
    {"player_a": '110', "player_b": '111'},
    {"player_a": '111', "player_b": '000'},
    {"player_a": '111', "player_b": '001'},
    {"player_a": '111', "player_b": '010'},
    {"player_a": '111', "player_b": '011'},
    {"player_a": '111', "player_b": '100'},
    {"player_a": '111', "player_b": '101'},
    {"player_a": '111', "player_b": '110'},
]

