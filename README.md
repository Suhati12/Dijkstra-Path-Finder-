# Dijkstra Path Finder GUI

A Python GUI application that implements Dijkstra's shortest path algorithm with an interactive interface.

#  Technologies Used
-  Python
- Tkinter (for GUI)
- Dijkstra Algorithm

#  Features

- **Create Nodes**: Add cities/locations as nodes
- **Add Edges**: Connect nodes with weighted edges (distances)
- **Find Shortest Path**: Select source and destination to find the optimal path
- **Visual Display**: Shows shortest path, total cost, and highlighted route

#  How to Run

```cmd
python dijkstra_gui.py


#  Usage

1. **Add Nodes**: Enter node names (e.g., "CityA", "CityB") and click "Add Node"
2. **Add Edges**: Enter source, destination, and weight (distance), then click "Add Edge"
3. **Find Path**: Enter start and end nodes, click "Find Shortest Path"
4. **View Results**: The GUI displays the shortest path and total cost

#  Example

1. Add nodes: A, B, C, D
2. Add edges:
   - A <-> B (weight: 4)
   - A <-> C (weight: 2)
   - B <-> D (weight: 5)
   - C <-> D (weight: 1)
3. Find path from A to D
4. Result: A -> C -> D (Total Cost: 3)
