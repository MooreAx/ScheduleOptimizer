'''

Next steps as follows:
1) automate preparation of input file (available pairings)
2) export results to excel file
3) all for additional constraints
    -- include / exclude certain pairings
    -- include training events / ground school / sim
    -- no pairings on selected days
4) include previous month's schedule, as working days constraints are rolling

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
def brute_force_optimize(pairings, min_credits, max_credits, top_n=12):
    best_combinations = []  # List to store top n combinations
    
    count_combinations = 0
    count_acceptable_combinations = 0

    for qty in range(1, len(pairings) + 1):
        for combination in itertools.combinations(pairings, qty):
            count_combinations += 1

            # Check for overlap
            if all(not is_overlapping(p1, p2) for i, p1 in enumerate(combination) for j, p2 in enumerate(combination) if i < j):
                total_credits = sum(p["Credits"] for p in combination)
                
                # Check if total credits meet the required range
                if total_credits >= min_credits and total_credits <= max_credits:
                    if has_consecutive_workdays_violating_limit(list(combination), 6):
                        continue  # Skip this combination if it violates the consecutive workdays rule
                    
                    count_acceptable_combinations += 1
                    # Calculate days off
                    consecutive_days_off = max_consecutive_days_off(list(combination))
                    
                    # Add to best combinations if it has more days off or if the list has fewer than top_n combinations
                    if len(best_combinations) < top_n:
                        best_combinations.append((combination, consecutive_days_off, total_credits))
                        best_combinations.sort(key=lambda x: x[1], reverse=True)  # Sort by max days off
                    elif consecutive_days_off > best_combinations[-1][1]:
                        best_combinations[-1] = (combination, consecutive_days_off, total_credits)
                        best_combinations.sort(key=lambda x: x[1], reverse=True)  # Sort by max days off

    print(f"\n\n{count_combinations} combinations checked. {count_acceptable_combinations} combinations acceptable.")
    
    return best_combinations

# Example usage
min_credits = 80
max_credits = 84

# Call the brute_force_optimize function
best_combinations = brute_force_optimize(Pairings, min_credits, max_credits)

# Function to generate the day matrix
def generate_day_matrix(best_combinations, month_start_date):
    days_in_month = (month_start_date.replace(month=month_start_date.month+1) - timedelta(days=1)).day
    days = [month_start_date + timedelta(days=i) for i in range(days_in_month)]

    # Create an empty matrix for the days and pairings
    matrix = [["" for _ in range(len(best_combinations))] for _ in range(days_in_month)]

    for col_idx, (combination, _, _) in enumerate(best_combinations):
        for p in combination:
            start_day_idx = (p["Start"] - month_start_date).days
            end_day_idx = (p["End"] - month_start_date).days
            for day_idx in range(start_day_idx, end_day_idx + 1):
                matrix[day_idx][col_idx] = f"{p['Name']}"

    # Print the header
    print(f"{'Day':<10}", end=" | ")
    for col_idx in range(len(best_combinations)):
        print(f"Pairing {col_idx + 1:<12}", end=" | ")
    print()


    # Print the header row (Max consecutive days off)
    print(f"{' ' * 10}", end=" | ")  # Align with "Day" column
    for _, max_days_off, _ in best_combinations:
        print(f"Max CDO: {max_days_off:<11}", end=" | ")
    print()


    # Print the day matrix
    for day_idx, day in enumerate(days):
        print(f"{day.strftime('%a %d %b'):<10}", end=" | ")
        for col in matrix[day_idx]:
            print(f"{col:<20}", end=" | ")
        print()

# Example usage
min_credits = 80
max_credits = 84

# Assuming month_start_date is the first day of the month you want to check
month_start_date = date(2025, 3, 1)

# Output the day matrix

print("\n\n")

generate_day_matrix(best_combinations, month_start_date)