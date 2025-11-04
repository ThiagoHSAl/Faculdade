import os
from flask import Flask, render_template, request, jsonify
from search import plan

app = Flask(__name__)

# Directory containing the text files
maps_directory = 'maps'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_maps', methods=['GET'])
def get_maps():
    maps = {}
    try:
        # Check if the directory exists
        if os.path.exists(maps_directory):
            # Get a list of all files with a .txt extension
            txt_files = [f for f in os.listdir(maps_directory) if f.endswith('.txt')]

            for txt_file in txt_files:
                file_path = os.path.join(maps_directory, txt_file)

                # Read the content of the file
                with open(file_path, 'r') as file:
                    content = file.read()

                # Extract the filename without extension
                filename = os.path.splitext(txt_file)[0]

                # Add the content to the dictionary with filename as key
                maps[filename] = content

            response = jsonify({'result': 'success', 'maps': maps})
            response.headers.add("Access-Control-Allow-Origin", "*")

            return response
        else:
            return jsonify({'result': 'error', 'error_details': 'Directory not found'}), 404
        
    except Exception as e:
        error_message = {'result': 'error', 'error_details': str(e)}
        return jsonify(error_message), 500
    
@app.route('/start_search', methods=['GET'])
def start_search():
    try:
        # Get map, algorithm, and heuristic from query parameters
        map_content = request.args.get('map')
        alg = request.args.get('alg')
        heuristic = request.args.get('heuristic')
        
        # --- NOVO: Recebe o nome do mapa como um parâmetro a mais ---
        map_name = request.args.get('map_name')

        # Plan the path
        path, path_cost, visited = plan(map_content, alg, heuristic)

        # Os prints no terminal continuarão funcionando
        print("Map Name:", map_name)
        print("Algorithm:", alg)
        print("Heuristic:", heuristic)
        print("Number of visited nodes:", len(visited))
        print("Path length:", len(path))
        print("Path cost:", path_cost)

        # --- NOVO: Bloco de código para salvar os resultados em um arquivo ---
        # O 'a' significa 'append', para adicionar ao final do arquivo sem apagar o conteúdo anterior.
        with open('resultados_busca.txt', 'a', encoding='utf-8') as f:
            f.write(f"----------------------------------------\n")
            f.write(f"Mapa: {map_name}\n")
            f.write(f"Algoritmo: {alg}\n")
            f.write(f"Heuristica: {heuristic or 'N/A'}\n")
            f.write(f"Nos Visitados: {len(visited)}\n")
            f.write(f"Tamanho do Caminho: {len(path)}\n")
            f.write(f"Custo do Caminho: {path_cost}\n\n")
        # --- FIM DO NOVO BLOCO ---

        # convert visited to a list
        visited = list(visited)

        # Perform search algorithm logic here with map_name and algorithm_name
        response = jsonify({'result': 'success', 'path': path, 'visited': visited})
        response.headers.add("Access-control-allow-origin", "*")

        return response

    except Exception as e:
        return jsonify({'result': 'error', 'error_details': str(e)}), 500

@app.route('/save_map', methods=['GET'])
def save_map():
    try:
        # Get filename and content from query parameters
        map_name = request.args.get('map_name')
        map_data = request.args.get('map')

        # Write the content to a file
        with open(f'{maps_directory}/{map_name}.txt', 'w') as file:
            file.write(map_data)

        response = jsonify({'result': 'success'})
        response.headers.add("Access-Control-Allow-Origin", "*")

        return response

    except Exception as e:
        return jsonify({'result': 'error', 'error_details': str(e)}), 500


if __name__ == '__main__':
    # Use the SSL context for HTTPS
    app.run(host="0.0.0.0", port="5001", debug=True)
