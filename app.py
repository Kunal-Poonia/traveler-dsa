from flask import Flask, request, jsonify, render_template, send_from_directory
import heapq
import os

app = Flask(__name__)

# Hardcoded graph: nodes and weighted edges (distance in km)
graph = {
    'A': {'B': 2, 'D': 3},
    'B': {'A': 2, 'C': 4},
    'C': {'B': 4, 'D': 2},
    'D': {'A': 3, 'C': 2}
}

# Node metadata for frontend (type for filtering)
nodes = {
    'A': {'name': 'City Center', 'type': 'transport'},
    'B': {'name': 'Train Station', 'type': 'transport'},
    'C': {'name': 'Museum', 'type': 'attraction'},
    'D': {'name': 'Park', 'type': 'nature'}
}

# Mode-specific speed (km/h)
speeds = {
    'walking': 5,
    'cycling': 20,
    'driving': 60,
    'public': 40
}

def dijkstra(graph, start, end):
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
    
    # Reconstruct path
    path = []
    current_node = end
    while current_node is not None:
        path.append(current_node)
        current_node = previous[current_node]
    path.reverse()
    
    return path, distances[end]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/nodes')
def get_nodes():
    return jsonify(nodes)

@app.route('/route', methods=['POST'])
def get_route():
    data = request.get_json()
    start = data.get('start')
    end = data.get('end')
    mode = data.get('mode', 'walking')
    
    if start not in graph or end not in graph:
        return jsonify({'error': 'Invalid start or end point'}), 400
    
    path, distance = dijkstra(graph, start, end)
    if not path:
        return jsonify({'error': 'No route found'}), 404
    
    # Calculate time (distance / speed in hours, then convert to minutes)
    speed = speeds.get(mode, 5)  # Default to walking speed
    time = (distance / speed) * 60  # Convert hours to minutes
    
    return jsonify({
        'path': path,
        'distance': round(distance, 2),
        'time': round(time, 2)
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)