from flask import Flask, request, jsonify, render_template
import heapq
import os

app = Flask(__name__)

# Expanded graph: 20 nodes with weighted edges (distance in km)
graph = {
    'A': {'B': 2, 'E': 4, 'F': 3},              # Downtown
    'B': {'A': 2, 'C': 3, 'G': 5},              # Train Station
    'C': {'B': 3, 'D': 2, 'H': 4},              # Museum District
    'D': {'C': 2, 'I': 3, 'J': 5},              # Central Park
    'E': {'A': 4, 'F': 2, 'K': 6},              # Airport
    'F': {'A': 3, 'E': 2, 'G': 4, 'L': 5},      # Bus Terminal
    'G': {'B': 5, 'F': 4, 'H': 3, 'M': 6},      # Art Quarter
    'H': {'C': 4, 'G': 3, 'I': 2, 'N': 5},      # Lakefront
    'I': {'D': 3, 'H': 2, 'J': 4, 'O': 6},      # Botanical Gardens
    'J': {'D': 5, 'I': 4, 'P': 3},              # Zoo
    'K': {'E': 6, 'L': 3, 'Q': 5},              # Industrial Zone
    'L': {'F': 5, 'K': 3, 'M': 4, 'R': 6},      # Shopping District
    'M': {'G': 6, 'L': 4, 'N': 3, 'S': 5},      # Theater District
    'N': {'H': 5, 'M': 3, 'O': 4, 'T': 6},      # Beach
    'O': {'I': 6, 'N': 4, 'P': 3},              # Stadium
    'P': {'J': 3, 'O': 3, 'Q': 4},              # Amusement Park
    'Q': {'K': 5, 'P': 4, 'R': 3},              # Tech Hub
    'R': {'L': 6, 'Q': 3, 'S': 4},              # Food Market
    'S': {'M': 5, 'R': 4, 'T': 3},              # Cinema Row
    'T': {'N': 6, 'S': 3}                       # Pier
}

# Node metadata: name, type, and description
nodes = {
    'A': {'name': 'Downtown', 'type': 'transport', 'desc': 'Central hub of the city'},
    'B': {'name': 'Train Station', 'type': 'transport', 'desc': 'Main rail connection'},
    'C': {'name': 'Museum District', 'type': 'attraction', 'desc': 'Cultural exhibits'},
    'D': {'name': 'Central Park', 'type': 'nature', 'desc': 'Green oasis'},
    'E': {'name': 'Airport', 'type': 'transport', 'desc': 'International flights'},
    'F': {'name': 'Bus Terminal', 'type': 'transport', 'desc': 'Regional bus hub'},
    'G': {'name': 'Art Quarter', 'type': 'attraction', 'desc': 'Galleries and studios'},
    'H': {'name': 'Lakefront', 'type': 'nature', 'desc': 'Scenic waterfront'},
    'I': {'name': 'Botanical Gardens', 'type': 'nature', 'desc': 'Exotic plants'},
    'J': {'name': 'Zoo', 'type': 'attraction', 'desc': 'Wildlife exhibits'},
    'K': {'name': 'Industrial Zone', 'type': 'business', 'desc': 'Factories and offices'},
    'L': {'name': 'Shopping District', 'type': 'shopping', 'desc': 'Retail paradise'},
    'M': {'name': 'Theater District', 'type': 'entertainment', 'desc': 'Live performances'},
    'N': {'name': 'Beach', 'type': 'nature', 'desc': 'Sandy shores'},
    'O': {'name': 'Stadium', 'type': 'entertainment', 'desc': 'Sports and concerts'},
    'P': {'name': 'Amusement Park', 'type': 'entertainment', 'desc': 'Rides and fun'},
    'Q': {'name': 'Tech Hub', 'type': 'business', 'desc': 'Innovation center'},
    'R': {'name': 'Food Market', 'type': 'dining', 'desc': 'Local cuisine'},
    'S': {'name': 'Cinema Row', 'type': 'entertainment', 'desc': 'Movie theaters'},
    'T': {'name': 'Pier', 'type': 'attraction', 'desc': 'Ocean views'}
}

# Mode-specific speed (km/h)
speeds = {
    'walking': 5,
    'cycling': 20,
    'driving': 60,
    'public': 40
}

def dijkstra(graph, start, end):
    """Calculate shortest path using Dijkstra's algorithm."""
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    previous = {node: None for node in graph}
    pq = [(0, start)]
    
    while pq:
        current_distance, current_node = heapq.heappop(pq)
        if current_node == end:
            break
        if current_distance > distances[current_node]:
            continue
        
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))
    
    if distances[end] == float('infinity'):
        return None, None
    
    path = []
    current_node = end
    while current_node is not None:
        path.append(current_node)
        current_node = previous[current_node]
    path.reverse()
    return path, distances[end]

@app.route('/')
def index():
    try:
        return render_template('index.html')  # Ensure template is found
    except Exception as e:
        return f"Error rendering template: {str(e)}", 500

@app.route('/nodes')
def get_nodes():
    """Return all node metadata."""
    try:
        return jsonify(nodes)
    except Exception as e:
        return jsonify({'error': f'Failed to fetch nodes: {str(e)}'}), 500

@app.route('/route', methods=['POST'])
def get_route():
    """Calculate and return the shortest route."""
    data = request.get_json()
    start = data.get('start')
    end = data.get('end')
    mode = data.get('mode', 'walking')
    
    if not start or not end:
        return jsonify({'error': 'Start and end points are required'}), 400
    if start not in graph or end not in graph:
        return jsonify({'error': 'Invalid start or end point'}), 400
    
    path, distance = dijkstra(graph, start, end)
    if not path:
        return jsonify({'error': 'No route found between points'}), 404
    
    speed = speeds.get(mode, 5)
    time = (distance / speed) * 60  # Convert to minutes
    
    return jsonify({
        'path': path,
        'distance': round(distance, 2),
        'time': round(time, 2)
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)