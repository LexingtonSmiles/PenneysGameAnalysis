# Scoring Assessment and Test 
## Quick Setup:
The code to run to test is main.py

## Logic

To score the data we used the following functions:

- load_first_raw_file(): Loads in the first file in a folder whose name contains 'raw' using np.load

- count_raw_files(): Counts the number of files in the given folder whose filename contains 'raw'

- rename_raw_to_cooked(): Renames a single file starting with 'raw-deck' to 'cooked-deck'

- check_or_create_wins_df(): Checks if a CSV file exists in the folder. If yes, loads it as a DataFrame. If not, creates a blank DataFrame with rows from combos and scoring columns.

- score_deck(): Scores a single deck for both trick and card scoring.

- save_dataframe_to_csv(): Saves a pandas DataFrame to a CSV file.

- count_wins(): Given a DataFrame with results from a single deck, computes win/loss/draw counts for both game modes (tricks and cards).

- update_results(): Updates the cumulative results DataFrame with the new scores from scores_df.

These functions were then called within our function analyze(). 

Overall our scoring method works by analyzing one deck in one file at a time. Each deck is made up of booleans due to our data generation file but when we look at the deck in our Scoring file we transform the booleans into strings of 0s and 1s. Then we iterate through the deck and identify the number of cards and tricks each player gets based on their chosen combination. Then we add all of this information into one row of a DataFrame that will not be saved but will be used to add data to the results output. Then repeat for all of the decks in all of the files. Finally a new DataFrame is made from the first DataFrame that contains the information as to which player won with cards or tricks, in addition to the number of draws in trick or cards there is.

## Method
We arrived at this method by writing this code a few different ways. Originally we started by loading all of the decks into a DataFrame then iterating through this DataFrame to calculate the scores, however this required using two for loops which we realized would be slower than using a singular one to grab the deck, calculate the scores, and put this into a row in the DataFrame all at once. We also tested whether it would be faster and save more storage to calculate the scores from strings instead booleans. To test this we wrote code for both options then used a new function to calculate their runtimes and storage uses. In the end we calculated that it is more efficient to calculate the scores using the strings instead of booleans so we made sure to include this method in our final scoring file.