#! /usr/bin/env python
# (c) 2023 Lucas V. Hartmann, github.com/lhartmann
# License MIT

import copy
import pandas as pd

class Automaton:
	def __init__(self):
		self._E = {} # Event set {e: prop}
		self._X = {} # State set {x: prop}
		self._F = {} # Transition function F[x][e] => {x}
		self._x0 = None # Initial state {x}
	
	# Flattens any type of input to a set
	@staticmethod
	def _flatten(x):
		y = set()
		
		if isinstance(x,dict):
			x = set(x.keys())
		
		if isinstance(x,list) or isinstance(x,set):
			for i in x:
				y = y.union(Automaton._flatten(i))
		else:
			y.add(x)
		return y
	
	# Returns the set of states that may be accessed via empty strings
	def xxx_nd(self, xxx):
		Xr = set()
		add = Automaton._flatten(xxx)
		while len(add):
			Xr = Xr.union(add)
			addnext = set()
			for x in add:
				if '' in self._F[x]:
					addnext = addnext.union(self._F[x][''])
			add = addnext - Xr
		return Xr
	
	@staticmethod
	def read_csv(filename):
		table = pd.read_csv(filename, sep='\t', header=None)
		table = table.fillna("")
		return Automaton.parse(table)
	
	@staticmethod
	def read_ods(filename, sheet=None):
		table = pd.read_excel(filename, sheet or 0, header=None)
		table = table.fillna("")
		return Automaton.parse(table)
	
	def copy(self): 
		return copy.deepcopy(self)
	
	@staticmethod
	def parse(table):
		r = Automaton()
		Ne = int(len(table.columns)-2)
		Ns = int(table.size / (Ne+2) - 2)
	
		r._x0 = table.iat[0,0]
		r._X = {}
		r._E = {}
		r._F = {} # F[s][e] -> S
		
		if isinstance(r._x0, str):
			r._x0 = r._x0.split(',')
		else:
			r._x0 = set({r._x0})
	
		for s in range(Ns):
			state_name = table.iat[s+2, 0]
			state_prop = table.iat[s+2, 1] or ""
			r._X[state_name] = state_prop
	
		for e in range(Ne):
			event_name = table.iat[0, e+2]
			event_prop = table.iat[1, e+2] or ""
			r._E[event_name] = event_prop
		
		for s in range(Ns):
			state = table.iat[s+2, 0]
			r._F[state] = {}
			for e in range(Ne):
				event = table.iat[0, e+2]
				
				dest = table.iat[s+2,e+2]
				
				if dest == None or dest == "":
					continue
				
				if isinstance(dest, str):
					r._F[state][event] = set(dest.split(','))
				else:
					r._F[state][event] = set({ dest })
		return r
	
	def X(self):
		return set(self._F.keys())
	
	def Xm(self, mark="M"):
		return set([ x for x in self._X if mark in self._X[x]])

	def E(self):
		return set(self._E.keys())
	
	# Returns enabled events for a state or a set of states.
	def L(self, xxx):
		xxx = Automaton._flatten(xxx)
		
		eee = set()
		for x in xxx:
			eee = eee.union(set(self._F[x].keys()))
		return eee

	def count_arcs(self):
		return sum([len(E) for x,E in self._F.items() ])

	# Returns set of destinations from a set of states and set of events
	def FFF(self, xxx, eee):
		xxx = self.xxx_nd(xxx)
		eee = Automaton._flatten(eee)
		Xr = set()
		for x in xxx:
			for e in eee:
				if e in self._F[x]:
					Xr = Xr.union(self._F[x][e])
		return self.xxx_nd(Xr)
	
	# Deterministic version of above, returns a single state
	def F(self, x, e):
		Xr = self.FFF(x,e)
		if len(Xr) != 1:
			raise Exception(f"F({x},{e}) should return exactly one state.")
		return Xr.pop()
	
	def remove_states(self, Xd):
		r = self.copy()

		# Remove deleted states and all transitions FROM them
		for x in Xd:
			r._X.pop(x)
			r._F.pop(x)

		# Remove transitions TO deleted states
		for x in r._X:
			rm = set()
			for e in r._F[x]:
				r._F[x][e] = r._F[x][e] - Xd
				if len(r._F[x][e]) == 0:
					rm.add(e)
			for e in rm:
				r._F[x].pop(e)

		return r
	
	# Remove events replacing with empty string.
	# Result is usually non-deterministic.
	def remove_events(self, Ed):
		r = self.copy()

		# Adds empty transitions for uniformity
		for x in r._X:
			if "" not in r._F[x]:
				r._F[x][""] = set()
		
		for e in Automaton._flatten(Ed):
			# Rename events to empty string
			if e in r._E:
				r._E.pop(e)
				r._E[""] = ""
			# Move transitions from e to "".
			for x in r._F:
				if e in r._F[x]:
					r._F[x][""] = r._F[x][""].union(r._F[x].pop(e))

		# Removes empty transitions
		for x in r._F:
			if len(r._F[x][""]) == 0:
				r._F[x].pop("")

		return r
	
	# Replaces all but selected events with the empty string,
	# Result is usually non-deterministic.
	def projection(self, Es):
		return remove_events(Automaton._flatten(self._E) - Automaton._flatten(Es));

	# Returns the accessible part of the automaton
	def Ac(self):
		Xa = set(self._x0)
		while True:
			Xan = self.FFF(Xa, self.L(Xa))
			if len(Xan - Xa) == 0:
				break
			Xa = Xa.union(Xan)
		return self.copy().remove_states(set(self._X.keys()) - Xa)
	
	# Returns the co-accessible part of the automaton
	def CoAc(self):
		Xc = self.Xm()
		added = True
		while added:
			added = False
			for x in set(self._X.keys()) - Xc:
				dest = self.FFF(x, self.L(x))
				if len(Xc.intersection(dest)) != 0:
					added = True
					Xc.add(x)
		return self.copy().remove_states(set(self._X.keys()) - Xc)
	
	def trim(self):
		return self.Ac().CoAc()
	
	def write_dot(self, filename, rankdir="LR", layout="dot", overlap=False, splines=True,
			sanitize = lambda x: x.replace('{','').replace('}','')
	):
		with open(filename, "w") as f:
			f.truncate()
			f.write("digraph {\n")
			f.write(f"\trankdir=\"{rankdir}\";\n")
			f.write(f"\tlayout=\"{layout}\";\n")
			f.write(f"\toverlap=\"{overlap}\";\n")
			f.write(f"\tsplines=\"{splines}\";\n")
			
			for state in self._X:
				shape = "doublecircle" if state in self.Xm() else "circle"
				f.write("\t\"%s\" [shape=%s, label=\"%s\"];\n" % (sanitize(state), shape, sanitize(state)))
			
			f.write("\tINITIAL_STATE_ENTRYPOINT[shape=none, label=\"\"];\n")
			for x0 in self._x0:
				f.write("\tINITIAL_STATE_ENTRYPOINT -> \"%s\"\n" % sanitize(x0))
			for state in self._F:
				for event in self._F[state]:
					for target in self._F[state][event]:
						f.write("\t\"%s\" -> \"%s\" [label=\"%s\"];\n" % (sanitize(state), sanitize(target), sanitize(event)))
			
			f.write("}\n");
	
	def write_plantuml(self, filename, sanitize = lambda x: x):
		with open(filename, "w") as f:
			f.truncate()
			f.write("@startuml\n")
			f.write("hide empty description\n")
			
			for x0 in self._x0:
				f.write(f"[*] --> {sanitize(x0)}\n")
			for state in self._F:
				for event in self._F[state]:
					for target in self._F[state][event]:
						f.write(f"{sanitize(state)} --> {sanitize(target)} : {sanitize(event)}\n")
			
			f.write("@enduml\n");
	
	# Non-deterministic version
	def eval(self, string, x0 = None):
		xxx = self._x0 if x0 == None else x0
		xxx = Automaton._flatten(xxx)
		for events in string:
			xxx = self.FFF(xxx, events)
		return xxx
	
	def cross(self,other):
		result = Automaton()
		
		# Result event set is intersection of inputs
		for e in self._E:
			if e in other._E:
				result._E[e] = self._E[e]
		
		# Result initial state is both initials
		ax0 = self._x0.copy().pop()
		bx0 = other._x0.copy().pop()
		result._x0 = set([f"{ax0}|{bx0}"])
		
		X = [] # Complete set of states
		
		pend = [(ax0,bx0)] # States pending expansion
		while len(pend):
			x = pend.pop()
			if x in X: continue
			#print("x:",x)
			X.append(x)
			result._F[f"{x[0]}|{x[1]}"] = {}
			
			# Expand events enabled on both inputs
			for e in self.L(x[0]) & other.L(x[1]):
				nx = (self.F(x[0], e), other.F(x[1], e))
				#print("nx:", nx)
				pend.append(nx)
				result._F[f"{x[0]}|{x[1]}"][e] = set([f"{nx[0]}|{nx[1]}"])
		
		for x in X:
			#print("x:", x)
			result._X[f"{x[0]}|{x[1]}"] = f"{self._X[x[0]]}|{other._X[x[1]]}"
		
		return result
	
	def parallel(self, other):
		a = self.copy()
		b = other.copy()
		
		# Add self loops on a, for events only on b
		for e in b._E.keys() - a._E.keys():
			a._E[e] = ""
			for x in a._F:
				a._F[x][e] = set([x])
		
		# Add self loops on b
		for e in a._E.keys() - b._E.keys():
			b._E[e] = ""
			for x in b._F:
				b._F[x][e] = set([x])
		
		return a.cross(b)
	
	def __mul__(self, other):
		return  self.cross(other)
	
	def __or__(self, other):
		return  self.parallel(other)
	
	def is_deterministic(self):
		for x in self._F:
			if "" in self._F[x] and self._F[x][""] != set([x]):
				return False
			for e in self._F[x]:
				if len(self._F[x][e]) > 1:
					return False
		return True
	
	def deterministic_equivalent(self, state_namer = lambda x: " ".join(sorted(list(x)))):
		r = Automaton()
		add = self.xxx_nd(self._x0) # Set of states
		r._x0 = { state_namer(add) }
		
		add = [add]
		while len(add) > 0:
			addnext = []
			for x in add:
				snx = state_namer(x)
				if snx in r._F:
					continue
				#print(f"Adding state {snx}:")
				r._F[snx] = {}
				for e in self.L(x)-{""}:
					tx = self.FFF(x, e)
					sntx = state_namer(tx)
					r._E[e] = self._E[e]
					r._F[snx][e] = {sntx}
					addnext.append(tx)
					#print(f"  F[...][{e}] -> {sntx}")
					
					##########
			add = addnext
		return r
	
	def write_cpp(self, filename, sanitize=lambda s: s):
		if not self.is_deterministic():
			raise "Automaton.write_cpp() requires a deterministic automaton."
		
		with open(filename, "w") as f:
			f.truncate()
			f.write("enum State_t {\n")
			for x in self._X:
				f.write(f"\t{sanitize(x)}, // {self._X[x]}\n")
			f.write("};\n\n")
			
			f.write("State_t update(State_t x) {\n")
			f.write("\tswitch(x) {\n")
			for x in self._F:
				f.write(f"\tcase ({sanitize(x)}):"+" {\n")
				for e in self._F[x]:
					f.write(f"\t\tif (Event_{sanitize(e)}()) return {sanitize(self._F[x][e].copy().pop())};\n")
				f.write(f"\t\tbreak;\n\n")
			f.write(f"\tdefault: return {sanitize(self._x0.copy().pop())};\n")
			f.write("\t}\n")
			f.write("\treturn x;\n")
			f.write("}\n")
	
	# Gives an event priority over the others.
	# In other words, for every state where the event is enabled, make if the only enabled one.
	def prioritize(self, e):
		r = self.copy()
		for x in r._F:
			if e in r._F[x]:
				r._F[x] = {e: r._F[x][e]}
		return r
	
	# Renames states based on a mapper, which may be a function or a dictionary.
	def rename_states(self, mapper):
		r = self.copy()

		M = lambda x: mapper(x) if callable(mapper) else mapper[x] if x in mapper else x
		F = {}
		for x in r._F:
			mx = M(x)
			F[mx] = {}
			for e in r._F[x]:
				F[mx][e] = set()
				for tx in r._F[x][e]:
					F[mx][e].add(M(tx))
		r._F = F
		r._X = {M(x):p for (x,p) in r._X}
		r._x0 = set([ M(x) for x in r._x0 ])
		return r
