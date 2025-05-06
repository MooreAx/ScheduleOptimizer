

from BruteForce import best_combinations
from datetime import datetime, timedelta, date
import calendar
import pandas as pd


# Function to generate the day matrix
def generate_day_matrix(best_combinations, month_start_date):

    days_in_month = calendar.monthrange(month_start_date.year, month_start_date.month)[1]

    #create list of days
    days = [month_start_date + timedelta(days=i) for i in range(days_in_month)]

    # Create an empty matrix for the days and pairings
    matrix = [["" for _ in range(len(best_combinations))] for _ in range(days_in_month)]

    for col_idx, (combination, _, _) in enumerate(best_combinations):
        for p in combination:
            start_day_idx = (p["Start"] - month_start_date).days
            end_day_idx = (p["End"] - month_start_date).days
            for day_idx in range(start_day_idx, end_day_idx + 1):
                matrix[day_idx][col_idx] += f"{p['Name']}"

    max_solns = 10

    # Print the header
    print(f"{'Day':<10}", end=" | ")
    for col_idx in range(min(len(best_combinations), max_solns)):
        print(f"Pairing {col_idx + 1:<12}", end=" | ")
    print()


    # Print the header row (Max consecutive days off)
    print(f"{' ' * 10}", end=" | ")  # Align with "Day" column
    i=0
    for _, max_days_off, _ in best_combinations:
        i += 1
        if i > max_solns:
            continue
        print(f"Max CDO: {max_days_off:<11}", end=" | ")

    print()

    #reduce the size
    truncated_matrix = [row[:10] for row in matrix]

    # Print the day matrix
    for day_idx, day in enumerate(days):
        print(f"{day.strftime('%a %d %b'):<10}", end=" | ")
        for col in truncated_matrix[day_idx]:
            print(f"{col:<20}", end=" | ")
        print()


# Assuming month_start_date is the first day of the month you want to check
month_start_date = date(2025, 6, 1)

# Output the day matrix

print("\n\n")

generate_day_matrix(best_combinations, month_start_date)



def create_schedule_dict(combination, start_date, end_date):

    #date range
    date_range = pd.date_range(start_date, end_date)

    #create a dictionary where the key is the date
    schedule_dict = {day: "" for day in date_range}

    for p in combination:

        #date range
        pairing_days = pd.date_range(p["Start"], p["End"])

        for day in pairing_days:
            schedule_dict[day] += p["Name"].strip()
    
    return(schedule_dict)


def create_dict_list(combinations):
    schedule_dicts = []

    start = datetime(2025,6,1)
    end = datetime(2025,6,30)

    for (c, _, _) in combinations:

        schedule_dict = create_schedule_dict(c, start, end)
        schedule_dicts.append(schedule_dict)

    return(schedule_dicts)


dict_list = create_dict_list(best_combinations)

final_df = pd.DataFrame(dict_list).T

print(final_df)


final_df.to_csv("output.csv")
