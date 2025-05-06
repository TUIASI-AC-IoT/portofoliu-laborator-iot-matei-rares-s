import os

import uuid
from flask import Flask, request, jsonify

app = Flask(__name__)

app.config['DEBUG'] = True


DIRECTOR_PATH="files"
@app.route('/files', methods=["GET"])
def getfiles():
    print(os.listdir(DIRECTOR_PATH))
    return os.listdir(DIRECTOR_PATH)


@app.route('/files', defaults={'path': ''})
@app.route('/files/<path:file_path>', methods=["GET"], defaults={'path': ''})
def get_file_by_path(file_path):
    print("oki")
    try:
        print(DIRECTOR_PATH+f'/{file_path}')
        with open(DIRECTOR_PATH+f'/{file_path}', 'r') as f:
            content = f.read()
        return {"name": file_path, "content": content}
    except FileNotFoundError:
        return {"error": f"File '{file_path}' not found"}, 404


@app.route('/files', defaults={'path': ''})
@app.route('/files/<path:file_path>', methods=["PUT"]) #creare 200/replace 204
def createfilewithname(file_path):
    data = request.get_json()
    content = data['content']

    if os.path.exists(DIRECTOR_PATH + f'/{file_path}'):
        return 'Great you reaplaced it, kind of', 204

    full_path = os.path.join(DIRECTOR_PATH, file_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    try:
        with open(full_path, 'w') as f:
            f.write(content)
        return jsonify({'message': f"File '{file_path}' created."}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/files', methods=["POST"]) #creare 200 (procesare la server)
def createfilewithcontent():
    #generare nume random
    data = request.get_json()
    content = data['content']
    try:
        generated_id = str(uuid.uuid4())
        file_path = f"Unnamed{generated_id}"
        with open(DIRECTOR_PATH+"/"+file_path, 'w') as f:
            f.write(content)
        return jsonify({'message': f"File '{file_path}' created."}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/files', defaults={'path': ''})
@app.route('/files/<path:file_path>', methods=["DELETE"])
def deletefilewithname(file_path):
    try:
        os.remove(DIRECTOR_PATH+"/"+file_path)
        if not os.path.exists(DIRECTOR_PATH+"/"+file_path):
            return jsonify({'message': f"File '{file_path}' deleted successfully."}), 200
        else:
            return jsonify({'error': 'File could not be deleted'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run()

