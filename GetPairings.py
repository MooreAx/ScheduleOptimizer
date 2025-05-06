# reads available pairings into a list

import pandas as pd

file_path = r"C:\Users\moore\OneDrive\Work\Calm Air\Bids\2025-06\JUNE TH FO 2025.xlsx"

df = pd.read_excel(
	file_path,
	engine="openpyxl",
	sheet_name = "PairingsClean"
	)

with pd.option_context("display.max_rows", None, "display.max_columns", None):
    print(df)

Pairings = [] # list for storing pairings

OPEN = False #set to true when a pairing has been opened but not closed
i = 0

for index, row in df.iterrows():

	if pd.isna(row["Flight"]):
		continue #skip to the next

	#Open a new pairing
	if not OPEN:
		OPEN = True
		i += 1
		Name = row["Flight"]
		Start = row["Date"].date()

	#if credits are >0, close the pairing
	if OPEN and row["Credits"] > 0:
		End = row["Date"].date()
		Credits = row["Credits"]
		ID = i
		ForceInclude = row["ForceInclude"]
		if pd.isna(ForceInclude):
			ForceInclude = "No"
		CountConsec = row["CountConsec"]
		if pd.isna(CountConsec):
			CountConsec = "Yes"



		
		#before appending as a new pairing, check that it is not effectively the same as another:

		found = False
		for p in Pairings:
			if p["Start"] == Start and p["End"] == End and p["Credits"] == Credits:
				
				#effectively the same as another pairing
				p["Name"] += " | " + Name
				found = True
				break

		if not found:
			Pairings.append({"ID": ID, "Name": Name, "Start": Start, "End": End, "Credits": Credits, "ForceInclude": ForceInclude, "CountConsec": CountConsec})
			print(f"ID = {ID}, Name = {Name}, Start = {Start}, End = {End}, Credits = {Credits}, ForceInclude: {ForceInclude}, CountConsec: {CountConsec}")

		OPEN = False