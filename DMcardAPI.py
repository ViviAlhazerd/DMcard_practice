from quart import Quart, request, jsonify, send_from_directory
import os
import aiohttp

app = Quart(__name__)

# Railway Volumeのパス
volume_path = os.getenv("RAILWAY_VOLUME_PATH", "/image")
image_dir = os.path.join(volume_path, "images")
os.makedirs(image_dir, exist_ok=True)  # ディレクトリがない場合は作成

# 保存されたファイルをJSONで返す
@app.route('/list_images', methods=['GET'])
async def list_images():
    try:
        # Volume内の画像ディレクトリの内容を取得
        files = os.listdir(image_dir)

        # ファイル名をバイト列として処理してUTF-8にデコード
        decoded_files = [file.encode().decode('utf-8') for file in files]

        return jsonify({'files': decoded_files}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to list files: {e}'}), 500

# 指定された画像を表示
@app.route('/images/<filename>', methods=['GET'])
async def serve_image(filename):
    try:
        # ファイルが存在する場合に返す
        return await send_from_directory(image_dir, filename)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

# 非同期で画像を保存
@app.route('/save_image', methods=['POST'])
async def save_image():
    try:
        # リクエストからデータを取得
        data = await request.json
        if not data or 'url' not in data or 'filename' not in data:
            return jsonify({'error': 'Invalid request. "url" and "filename" are required.'}), 400

        image_url = data['url']
        filename = data['filename']

        # 保存先のパスを構築
        save_path = os.path.join(image_dir, filename)

        # 非同期で画像をダウンロード
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    # ファイルを非同期で保存
                    with open(save_path, 'wb') as file:
                        while True:
                            chunk = await response.content.read(1024)  # 非同期でデータを読み込む
                            if not chunk:
                                break
                            file.write(chunk)
                    return jsonify({'message': 'Image saved successfully', 'path': save_path}), 200
                else:
                    return jsonify({'error': f'Failed to download image: HTTP {response.status}'}), 500

    except aiohttp.ClientError as e:
        return jsonify({'error': f'Failed to download image: {e}'}), 500
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {e}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
