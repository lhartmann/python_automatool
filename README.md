# python_automatool
Automaton build and analysis tooling for python.

# Quickstart

Install using pip:
```bash
pip install automatool
```

Download and run example:
```bash
git clone https://github.com/lhartmann/python_automatool automatool
cd automatool/examples
python3 01-basic.py
```

Then check the several `.dot` outputs using xdot.

# Defining Automatons

Automatons are defined in spreadsheets representing the transition table:
- States are lines, events are columns.
- The first line/column specifies the names of the events/states.
- The second line/column specifies the properties of the events/states.
- The initial state is defined on the first cell.
- Marked states should have "M" as their properties.
- Timed events should specify the lifetime as the property.
- Transition table is specified from third row/column on.

<table>
<tr><th>Initial state</th><th>Events</th><th>Event 1</th><th>Event 2</th><th>...</th><th>Event n</th></tr>
<tr><th>"States"</th><th>"Properties"</th><th>E1 properties</th><th>E2 properties</th><th>...</th><th>En properties</th></tr>
<tr><td>State 1</td><td>S1 properties</td><td>target</td><td>target</td><td>...</td><td>target</td></tr>
<tr><td>State 2</td><td>S2 properties</td><td>target</td><td>target</td><td>...</td><td>target</td></tr>
<tr><td>...</td><td>...</td><td>...</td><td>...</td><td>...</td><td>...</td></tr>
<tr><td>State m</td><td>Sm properties</td><td>target</td><td>target</td><td>...</td><td>target</td></tr>
</table>

# Reading and writing

```python
from automatool import Automaton
a = Automaton.read_ods('file.ods', 'Sheet 1') # Load from file
a.write_dot('file.dot')           # Saves for use with graphviz
a.write_plantuml('file.uml')      # Saves for use with PlantUML
b = a.copy()                      # Creates an independent copy
```

# Operations on Automatons

**Accessible automaton**: Returns a new automaton containing only states reachable from the initial one.

```python
b = a.Ac()
```

**Co-accessible automaton**: Return a new automaton containing only states that can reach a marked state.

```python
b = a.CoAc()
```

**Trim automaton**: Returns a new automaton containing only states that are both accessible and co-accessible.

```python
b = a.trim()
```

**Cross-parallel, or fully-parallel**: Returns an automata where any events can only happen if exist and enabled on both sources. Private events existing on a single source are removed and blocked.

```python
c = a.cross(b) # As a method
m = n * o * p  # As an expression
```

**Parallel**: Returns an automata where common events can only happen if exist and enabled on both sources. Private events existing on a single source are preserved, and do not affect the other automaton.

```python
c = a.parallel(b) # As a method
m = n | o | p     # As an expression
```

**Remove events**: Makes removed events non-observable, replacing them with the null-word. Generally result in a non-deterministic automaton.

```python
b = a.remove_events(["e0", "e1"])
```

**Remove states**: Removes states from an automaton. May make some states inaccessible.

```python
b = a.remove_states(["x0", "x1"])
```

**Deterministic equivalent**: Evaluates the automaton taking into considerations all null-word events, and events that can lead to multiple states. Returns an automaton that models the uncertainty between states A and B as a new state AB.

```python
print(a.is_detetrministic()) # False
b = a.deterministic_equivalent()
print(b.is_detetrministic()) # True
```

**Prioritize event**: When describing software controllers, an action event will always take place before any other input check, in other words, it will be fired immediately when enabled. Priorizing an event will ensure that, on states where it is enabled, it is the only one enabled. Useful fom simplifying analysis, as it may reduce the number of accessible states.

```python
b = a.prioritize('e6')
```

**Rename states**: State names are usally long after composition operations or deterministic-equivalent is obtained. States can be renamed by passing a function or a dictionary as a mapper.

```python
# On parallel composition names are joined with '|'
m = a | b | c
# Using a dictionary
n = m.rename_states({
    'a0|b1|c2': 's012',
    'a0|b3|c1': 's031'
})
# Using a callable lambda
n = m.rename_states(lambda s : s.replace('|', ''))

```
