# python_automatool
Automaton build and analysis tooling for python.

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

```
a = Automaton()                   # Creates an instace
a.read_ods('file.ods', 'Sheet 1') # Loads from file
a.write_dot('file.dot')           # Saves for use with graphviz
a.write_plantuml('file.uml')      # Saves for use with PLantUML
b = a.copy()                      # Creates an independent copy
```

# Operations on Automatons

**Accessible automaton**: Returns a new automaton containing only states reachable from the initial one.

```b = a.Ac()```

**Co-accessible automaton**: Return a new automaton containing only states that can reach a marked state.

```b = a.CoAc()```

**Trim automaton**: Returns a new automaton containing only states that are both accessible and co-accessible.

```b = a.trim()```

**Cross-parallel, or fully parallel**: 

```c = a.cross(b)```
