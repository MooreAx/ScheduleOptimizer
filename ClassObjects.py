class Pairing:
	def __init__(self, name, start, end, credits, force_include, count_consec):
		self.name = name
		self.start = start
		self.end = end
		self.credits = credits
		self.force_include = force_include
		self.count_consec = count_consec
		
	# returns a printable representation of the object
	def __repr__(self):
		return(f"Pairing({self.name}, {self.start}, {self.end}, {self.credits}, {self.force_include}, {self.count_consec})")

class Schedule:
	def __init__():
		self.Pairings = []

		def add_pairing(self, pairing):
			if isinstance(pairing, Pairing):
				self.flights.append(pairing)
			else:
				raise TypeError("expected Pairing object")

	@property
	def count_pairings(self):
		return len(self.Pairings)

	@property
	def credits(self):
		return sum(pairing.credits for pairing in self.Pairings)

	@property
	def MCDO(self):
		self.Pairings.sort(key=lambda p: p.start)
		
		max_days_off = 0
		for i in range(1, len(self.Pairings)):



