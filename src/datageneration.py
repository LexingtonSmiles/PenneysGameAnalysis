import pandas as pd
import numpy as np
import random
import os
import re


seed = 0

def generate_decks(n: int, seed: int):
    """
    Creates n by 52 array of n amount of shuffled decks each containing 26 Trues and 26 Falses
    """
    rng = np.random.default_rng(seed)
    
    # base deck
    deck = np.array([True] * 26 + [False] * 26)
    
    # generates n random permutations of indices [0..51]
    idx = np.array([rng.permutation(52) for _ in range(n)])
    
    # applies permutations to deck
    arr = deck[idx]
    
    return arr

def num_of_decks_per_file(tot_n:int, max_decks:int):
    """
    calculate the number of full files there will be and how many leftover decks there will be to go into the file
    """
    #calculate number of files that will be filled to their max deck size
    full_files = tot_n // max_decks
    #calculate the number of decks to go in the final file that will not be full
    leftover = tot_n % max_decks
    return full_files, leftover

def filepath_raw(seed: int, num_of_decks: int,PATH_DATA: str):
    """
    generate file name for each individual deck
    """
    #create filename based on the random seed and number of decks in the file
    filename = (f'raw-deck_seed{seed}_num_of_decks{num_of_decks}.npy')
    #join the filepath previously listed with the new name
    raw_filepath = os.path.join(PATH_DATA, filename)
        
    return raw_filepath

def savefile(decks: np.array, filepath: str):
    """
    save n decks to a .npy file with a specific file destination
    """
    #get the directory from the full filepath
    directory = os.path.dirname(filepath)
    #if the directory part is not empty and it doesn't exist then create it
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    #save the numpy array to the specified .npy file
    np.save(filepath, decks)
    return
    
def find_next_seed(PATH_DATA:str) -> int:
    """
    Scans all files in PATH_DATA and finds the highest seed number
    in filenames formatted like:
        'raw-deck_seed{seed}_num_of_decks{n}.npy'
        'cooked-deck_seed{seed}_num_of_decks{n}.npy'
    
    Returns the next unused seed (max + 1), or 0 if no files exist.
    """
    pattern = re.compile(r"^(?:raw|cooked)-deck_seed(\d+)_num_of_decks\d+\.npy$")
    seeds = []

    for fname in os.listdir(PATH_DATA):
        match = pattern.match(fname)
        if match:
            seeds.append(int(match.group(1)))

    return max(seeds) + 1 if seeds else 0
    
#@measure_rw
def make_files(tot_n:int, PATH_DATA: str, max_decks:int = 10000):
    """
    use generate function to make the decks for each file then use save function to 
    save each file with the filename function
    """
    #use num of files to determine how many decks go in each file
    full_files, leftover = num_of_decks_per_file(tot_n = tot_n, max_decks = max_decks)

    filepaths = [] 
    
    #find initial seed for generation
    seed = find_next_seed(PATH_DATA)
    
    for i in range(full_files):
        #make a placeholder for all decks about to go into the file
        full_storage = []
        
        
        
        #generate decks for the full files
        if full_files != 0:
            
            full_storage.append(generate_decks(max_decks, seed))
            
            #make filepath/name
            filepath = filepath_raw(seed, max_decks, PATH_DATA)

            #use save file raw to save the file with all the decks in it  
            savefile(full_storage, filepath)

            filepaths.append(filepath)

            #update seed num for next file
            seed += 1



    if leftover != 0:
        #make new placeholder for decks about to go into leftover file
        leftover_storage = []
            
        #generate decks for the not full files
        seed = find_next_seed(PATH_DATA)
        leftover_storage.append(generate_decks(leftover, seed))

        #make filepath/name
        filepath = filepath_raw(seed, leftover, PATH_DATA)

        #use save file raw to save the file with all the decks in it
        savefile(leftover_storage, filepath)

        filepaths.append(filepath)


    file_sizes = [os.path.getsize(path) for path in filepaths if os.path.exists(path)]

    return filepaths, file_sizes