import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors
import os
import re

# ----------------------------------------------------------
# Utility Functions
# ----------------------------------------------------------

def find_scoring_analysis_filename(folder_path):
    """
    Searches the given folder for the first .csv file and returns its full path.

    Parameters:
        folder_path (str): Path to the folder containing the scoring analysis files.

    Returns:
        str: Full file path to the first .csv file found.

    Raises:
        FileNotFoundError: If no .csv file is found in the folder.
    """
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            full_path = os.path.join(folder_path, filename)
            return full_path
        else:
            continue
    raise FileNotFoundError


def find_num_of_decks_scored(filename):
    """
    Extracts the number of decks (N) from a filename following the pattern '...=N.csv'.

    Parameters:
        filename (str): Filename containing '=N' before the extension.

    Returns:
        str: Extracted number of decks as a string.
    """
    n = filename.split('=')[1].split(".")[0]
    return n


def load_scoring_analysis(path):
    """
    Loads the scoring analysis CSV file and formats player codes from binary to colors.

    Parameters:
        path (str): Full path to the scoring analysis CSV file.

    Returns:
        pd.DataFrame: DataFrame with player IDs formatted (0→B, 1→R).
    """
    df = pd.read_csv(path, converters={'p1': str, 'p2': str})
    
    # Convert binary representation (0/1) to color labels (B/R)
    df["p1"] = df["p1"].str.replace('0', 'B').str.replace('1', 'R')
    df["p2"] = df["p2"].str.replace('0', 'B').str.replace('1', 'R')
    
    return df


def calculate(p1_wins: str, p2_wins: str, draws: str, df: pd.DataFrame):
    """
    Calculates win rates and draw rates for each pair of players.

    Parameters:
        p1_wins (str): Column name for player 1 wins.
        p2_wins (str): Column name for player 2 wins.
        draws (str): Column name for draws.
        df (pd.DataFrame): DataFrame containing scoring data.

    Returns:
        pd.DataFrame: Updated DataFrame with win rates and draw rates.
    """
    # Compute total rounds played
    df["total_wins"] = df[p1_wins] + df[p2_wins] + df[draws]

    # Compute probabilities
    df["p1_win_rate"] = df[p2_wins] / df["total_wins"]
    df["draw_rate"] = df[draws] / df["total_wins"]

    # Round to two decimals for cleaner presentation
    df["p1_win_rate"] = df["p1_win_rate"].round(2)
    df["draw_rate"] = df["draw_rate"].round(2)

    return df


def matrix(df):
    """
    Creates formatted matrices for heatmap visualization.

    One matrix holds numeric win rates (for color values), and another holds 
    text annotations showing win and draw percentages.

    Parameters:
        df (pd.DataFrame): DataFrame with win/draw rate calculations.

    Returns:
        tuple: (value_matrix, annotation_matrix)
    """
    # Format text as "Win% (Draw%)"
    df["annotation"] = df.apply(lambda row: f'{int(row["p1_win_rate"]*100)} ({int(row["draw_rate"]*100)})', axis=1)

    # Extract all unique player combinations for matrix axes
    p1_values = sorted(df["p1"].unique())
    p2_values = sorted(df["p2"].unique())

    # Initialize annotation matrix with NaN
    annotation_matrix = pd.DataFrame(index=p1_values, columns=p2_values)

    # Fill in annotation values (e.g., "65 (10)")
    for _, row in df.iterrows():
        annotation_matrix.loc[row["p1"], row["p2"]] = row["annotation"]

    # Pivot numerical data to create a value matrix for coloring
    value_matrix = df.pivot(index="p1", columns="p2", values="p1_win_rate")

    return value_matrix, annotation_matrix


def blackbox(value_matrix, ax):
    """
    Draws black borders around the cells representing the maximum win rate 
    in each row (i.e., best-performing matchups).

    Parameters:
        value_matrix (pd.DataFrame): Numeric win rate matrix.
        ax (matplotlib.axes.Axes): Matplotlib axis object for the heatmap.
    """
    for row_idx in value_matrix.index:
        row = value_matrix.loc[row_idx]
        max_cols = row[row == row.max()].index  # Accounts for ties

        # Draw a black rectangle around the best cells
        for col_idx in max_cols:
            ax.add_patch(
                patches.Rectangle(
                    (value_matrix.columns.get_loc(col_idx), value_matrix.index.get_loc(row_idx)),
                    1, 1, fill=False, edgecolor='black', lw=3
                )
            )


# ----------------------------------------------------------
# Main Heatmap Creation
# ----------------------------------------------------------

def make_heatmap(df_folder: str, heatmap_folder: str, t_or_c: str = 'Tricks'):
    """
    Generates and saves a heatmap for either 'Tricks' or 'Cards' results.

    Parameters:
        df_folder (str): Folder containing scoring analysis CSV file.
        heatmap_folder (str): Folder to save the generated heatmap.
        t_or_c (str): Type of analysis ('Tricks' or 'Cards').
    """
    # Find and load the scoring data
    filename = find_scoring_analysis_filename(df_folder)
    N = find_num_of_decks_scored(filename)
    df = load_scoring_analysis(filename)

    # Compute statistics based on analysis type
    if t_or_c == 'Tricks':
        df = calculate('p1_wins_tricks', 'p2_wins_tricks', 'draws_tricks', df)
    elif t_or_c == 'Cards':
        df = calculate('p1_wins_cards', 'p2_wins_cards', 'draws_cards', df)
    else:
        raise ValueError("Invalid input: must be 'Tricks' or 'Cards'")
    
    # Create value and annotation matrices
    value_matrix, annotation_matrix = matrix(df)

    # Define colormap and mask invalid entries
    cmap = sns.color_palette("YlOrBr", as_cmap=True)
    cmap.set_bad(color='lightgray')
    masked_matrix = value_matrix.mask(value_matrix == -1)

    # Create the heatmap figure
    plt.figure(figsize=(10, 8))
    ax = sns.heatmap(
        masked_matrix,
        annot=annotation_matrix,
        fmt='',
        cmap=cmap,
        cbar=False,
        linewidths=1,
        linecolor='white',
        square=True
    )
        
    # Highlight best matchups
    blackbox(value_matrix, ax)

    # Titles and labels
    plt.title(f"My Chance of Win(Draw) \nby {t_or_c} \nN={N}")
    plt.ylabel("Opponent choice")
    plt.yticks(rotation=0)
    plt.xlabel("My choice")
    plt.tight_layout()

    # Save the figure as an SVG file
    plt.savefig(f"{heatmap_folder}/By{t_or_c}.svg", format="svg")


def heatmap(df_folder: str, heatmap_folder: str):
    """
    Generates both Trick-based and Card-based heatmaps for the scoring data.

    Parameters:
        df_folder (str): Folder containing scoring analysis CSV file.
        heatmap_folder (str): Folder to save heatmaps.
    """
    make_heatmap(df_folder, heatmap_folder, 'Tricks')
    make_heatmap(df_folder, heatmap_folder, 'Cards')
    return