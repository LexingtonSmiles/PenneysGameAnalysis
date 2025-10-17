# Data Generation and Storage Assessment and Test 
## Quick Setup:
The code to run to test for oneself (hi professor) is in /code, titled run_tests.py

## Method

We have three distinct comparisons we want to test for data generation or storage.
These include:
- the way we shuffle decks:
  - (a)generating random indices
    
    vs.
  - (b)flattening the n decks into a single list then shuffling. splitting the list into num arrays while preserving the original deck size
    
- detecting seed to use for deck generation:
  - (c)scanning each file in the data folder and returning the next highest integer
    
    vs
  - (d)storing a seed variable and updating with +1 each time a file is generated
  
- the storage of decks using:
  - (e)booleans
    
    vs
  - (f) 0s and 1s
 
Test 1: compares storage of deck methods- Booleans vs 0s and 1s: 
permutation 1 vs permutation 3.

Test 2: compares shuffle decks methods: 
permutation 3 vs permutation 5

Test 3: compares seed detection: 
Permutation 3 or 5 vs permutation 7



Permutation 1: b, d, f

Permutation 3: b, d, e

Permutation 5: a, d, e

Permutation 7: a, c, e


##Results:

According to the tables recorded in all_test_results.md (open this file in vs code to see in proper formatting) permutation 5 performed the best. This permutation had the fastest run times and the smallest file sizes.