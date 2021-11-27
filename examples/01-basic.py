#! /usr/bin/env python

from automatool import Automaton

a = Automaton.read_csv("automatool/examples/automaton/a.csv")
a.write_dot("a.dot")

b = a.Ac()
b.write_dot("a_ac.dot")

b = a.CoAc()
b.write_dot("a_coac.dot")

b = a.trim()
b.write_dot("a_trim.dot")

a.remove_events(['e2'])
a.write_dot("a_non_deterministic.dot")

b = a.deterministic_equivalent()
b.write_dot("a_deterministic_equivalent.dot")

