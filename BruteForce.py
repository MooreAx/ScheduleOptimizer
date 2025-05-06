'''

Next steps as follows:
1) automate preparation of input file (available pairings)
2) export results to excel file --> done
3) all for additional constraints
    -- include / exclude certain pairings
    -- include training events / ground school / sim
    -- no pairings on selected days
4) include previous month's schedule, as working days constraints are rolling
5) add option to minimize "consecutive days on", i.e. opposite of "max days off

'''

import GetPairings
from datetime import datetime, timedelta, date
import itertools

Pairings = GetPairings.Pairings

# Function to check if two pairings overlap
def is_overlapping(p1, p2):
    return not (p1["End"] < p2["Start"] or p2["End"] < p1["Start"])

# Function to calculate days off between two pairings
def days_off_between(p1, p2):
    return (p2["Start"] - p1["End"]).days - 1

# Function to calculate the maximum days off for a combination of selected pairings
def max_consecutive_days_off(selected_pairings):
    selected_pairings.sort(key=lambda p: p["Start"])
    max_days_off = 0
    for i in range(1, len(selected_pairings)):
        days_off = days_off_between(selected_pairings[i-1], selected_pairings[i])
        if days_off > max_days_off:
            max_days_off = days_off
    return max_days_off

def min_days_on(selected_pairings):
    selected_pairings.sort(key=lambda p: p["Start"])
    start_first_pairing = selected_pairings[0]["Start"]
    end_last_pairing = selected_pairings[len(selected_pairings)-1]["End"]
    return (end_last_pairing - start_first_pairing).days

# Function to check if there are more than 6 consecutive workdays in a combination
def has_consecutive_workdays_violating_limit(selected_pairings, max_consecutive_workdays=6):
    selected_pairings.sort(key=lambda p: p["Start"])

    consecutive_workdays = 0
    prev_end_date = None
    
    for pairing in selected_pairings:
        if prev_end_date is None:
            prev_end_date = pairing["End"]
            consecutive_workdays = (pairing["End"] - pairing["Start"]).days + 1
            continue
        
        gap = (pairing["Start"] - prev_end_date).days
        if gap <= 1:
            consecutive_workdays += (pairing["End"] - pairing["Start"]).days + 1
        else:
            consecutive_workdays = (pairing["End"] - pairing["Start"]).days + 1
        
        if consecutive_workdays > max_consecutive_workdays:
            return True
        
        prev_end_date = pairing["End"]
    
    return False


# Function to brute force all combinations and keep the best 5
def brute_force_optimize(pairings, min_credits, max_credits, top_n=100, method = "minimize work"):
    best_combinations = []  # List to store top n combinations
    
    count_combinations = 0
    count_acceptable_combinations = 0

    max_off = 0
    min_on = 31

    for qty in range(4, 12):
        for combination in itertools.combinations(pairings, qty):
            count_combinations += 1

            # Check for overlap
            if all(not is_overlapping(p1, p2) for i, p1 in enumerate(combination) for j, p2 in enumerate(combination) if i < j):
                total_credits = sum(p["Credits"] for p in combination)
                
                # Check if total credits meet the required range
                if total_credits >= min_credits and total_credits <= max_credits:
                    if has_consecutive_workdays_violating_limit(list(combination), 4):
                        continue  # Skip this combination if it violates the consecutive workdays rule
                    
                    count_acceptable_combinations += 1
                    

                    if method == "maximize off":
                        # Calculate days off
                        consecutive_days_off = max_consecutive_days_off(list(combination))

                        if consecutive_days_off > max_off:
                            max_off = consecutive_days_off
                            print(f"max consecutive days off = {max_off}")
                        
                        # Add to best combinations if it has more days off or if the list has fewer than top_n combinations
                        if len(best_combinations) < top_n:
                            best_combinations.append((combination, consecutive_days_off, total_credits))
                            best_combinations.sort(key=lambda x: x[1], reverse=True)  # Sort by max days off
                        elif consecutive_days_off > best_combinations[-1][1]:
                            best_combinations.append((combination, consecutive_days_off, total_credits))
                            best_combinations.sort(key=lambda x: x[1], reverse=True)  # Sort by max days off
                    
                    elif method == "minimize work":
                         # Calculate days worked
                        consecutive_days_on = min_days_on(list(combination))

                        if consecutive_days_on < min_on:
                            min_on = consecutive_days_on
                            print(f"min consecutive days on = {min_on}")

                        # Add to best combinations if it has fewer days on, or if the list has fewer than top_n combinations
                        if len(best_combinations) < top_n:
                            best_combinations.append((combination, consecutive_days_on, total_credits))
                            best_combinations.sort(key=lambda x: x[1], reverse=False)  # Sort by min days on
                        elif consecutive_days_on < best_combinations[-1][1]:
                            best_combinations.append((combination, consecutive_days_on, total_credits))
                            best_combinations.sort(key=lambda x: x[1], reverse=False)  # Sort by min days off                       

            print(count_combinations)

    print(f"\n\n{count_combinations} combinations checked. {count_acceptable_combinations} combinations acceptable.")
    
    return best_combinations

# Example usage
min_credits = 60
max_credits = 67

# Call the brute_force_optimize function
 
best_combinations = brute_force_optimize(Pairings, min_credits, max_credits, method = "minimize work")


print("hi this is a test")