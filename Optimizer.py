import GetPairings
from datetime import timedelta
import pulp

# PARAMETERS
max_consecutive_days = 5

# Get Pairings from the external source
Pairings = GetPairings.Pairings

# Function to check if two Pairings overlap
def is_overlapping(p1, p2):
    return not (p1["End"] <= p2["Start"] or p2["End"] <= p1["Start"])

# Function to calculate days off between two Pairings
def days_off_between(p1, p2):
    return (p2["Start"] - p1["End"]).days - 1  # Days between the end of p1 and start of p2

# Create LP problem
prob = pulp.LpProblem("Pilot_Schedule_Bid", pulp.LpMaximize)

# Decision variables: x[i] = 1 if pairing i is selected
x = {p["ID"]: pulp.LpVariable(f"x_{p['ID']}", cat="Binary") for p in Pairings}

# Auxiliary variable to track the maximum consecutive days off
max_consecutive_off = pulp.LpVariable("max_consecutive_off", lowBound=0, cat="Integer")

# Objective function: Maximize credits + maximize max consecutive days off
prob += (
    max_consecutive_off  # Maximize max consecutive days off
)

# Constraints
prob += pulp.lpSum(p["Credits"] * x[p["ID"]] for p in Pairings) >= 80
prob += pulp.lpSum(p["Credits"] * x[p["ID"]] for p in Pairings) <= 84
prob += max_consecutive_off <= 18  

# Constraint: No overlapping Pairings
for i, p1 in enumerate(Pairings):
    for j, p2 in enumerate(Pairings):
        if i < j and is_overlapping(p1, p2):
            prob += x[p1["ID"]] + x[p2["ID"]] <= 1


# Reward longest consecutive days off between non-overlapping pairings
for i, p1 in enumerate(Pairings):
    for j, p2 in enumerate(Pairings):
        if i < j and not is_overlapping(p1, p2):  # Only consider non-overlapping pairings
            # Check if there are any intervening pairings that would disrupt the days off
            has_intervening_pairings = False
            for k, p3 in enumerate(Pairings):
                if k != i and k != j and p3["Start"] > p1["End"] and p3["Start"] < p2["Start"]:
                    has_intervening_pairings = True
                    break

            if not has_intervening_pairings:
                days_off = days_off_between(p1, p2)

                # Big-M method: Use a large constant (e.g., 1000) to simulate the product condition
                big_m = 1000  # Choose a sufficiently large constant

                # Add constraint to ensure max_consecutive_off is updated if both pairings are selected
                prob += max_consecutive_off >= days_off - big_m * (1 - x[p1["ID"]] - x[p2["ID"]])



# Solve problem
prob.solve()

# Get selected Pairings
selected_Pairings = [p for p in Pairings if pulp.value(x[p["ID"]]) == 1]
total_credits = sum(p["Credits"] for p in selected_Pairings)
max_off_days = pulp.value(max_consecutive_off)

# Output results
print("\nSelected Pairings:")
for p in selected_Pairings:
    print(f"Pairing {p['ID']}: {p['Start']} to {p['End']}, {p['Credits']} credits")

print(f"\nTotal Credits: {total_credits}")
print(f"Maximum Consecutive Days Off: {max_off_days}")



