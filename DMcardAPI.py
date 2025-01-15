from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# Railway Volumeのパス
volume_path = os.getenv("RAILWAY_VOLUME_PATH", "/image")
image_dir = os.path.join(volume_path, "images")
os.makedirs(image_dir, exist_ok=True)  # ディレクトリがない場合は作成

@app.route('/list_images', methods=['GET'])
def list_images():
    try:
        # Volume内の画像ディレクトリの内容を取得
        files = os.listdir(image_dir)

        # ファイル名をデコード
        decoded_files = [file.encode('utf-8').decode('unicode_escape') for file in files]

        return jsonify({'files': decoded_files}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to list files: {e}'}), 500


@app.route('/save_image', methods=['POST'])
def save_image():
    try:
        # リクエストからデータを取得
        data = request.json
        if not data or 'url' not in data or 'filename' not in data:
            return jsonify({'error': 'Invalid request. "url" and "filename" are required.'}), 400

        image_url = data['url']
        filename = data['filename']

        # 保存先のパスを構築
        save_path = os.path.join(image_dir, filename)

        # 画像をダウンロード
        response = requests.get(image_url, stream=True)
        response.raise_for_status()  # エラーを検出

        # ファイルを保存
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

        return jsonify({'message': 'Image saved successfully', 'path': save_path}), 200

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to download image: {e}'}), 500
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {e}'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
