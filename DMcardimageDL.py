import mysql.connector
import requests
from bs4 import BeautifulSoup
import os
# MySQL接続設定
db_config = {
    "host": "autorack.proxy.rlwy.net",
    "port": 14820,
    "user": "root",
    "password": "UbzlvtfvbaQvFrwXrfejFlbKzdoPBSBk",
    "database": "railway",
}




# 環境変数からVolumeのパスを取得
volume_path = os.getenv("RAILWAY_VOLUME_MOUNT_PATH", "/var/lib/mysql")
image_dir = os.path.join(volume_path, "images")

# ディレクトリ作成
if not os.path.exists(image_dir):
    os.makedirs(image_dir)

# 画像をダウンロードして保存する関数
def save_image(image_url, filename):
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()  # HTTPエラーがある場合は例外をスロー

        # 画像の保存パスを作成
        save_path = os.path.join(image_dir, filename)

        # 画像を保存
        with open(save_path, "wb") as image_file:
            for chunk in response.iter_content(1024):
                image_file.write(chunk)

        print(f"Image saved to: {save_path}")
        return save_path

    except Exception as e:
        print(f"Failed to save image: {e}")
        return None

# 画像のURLと保存するファイル名
image_url = "https://dm.takaratomy.co.jp/wp-content/card/cardimage/dm24rp4-S03.jpg"
filename = "超暴淵 ボジャガイスト.jpg"

# 画像保存
save_image(image_url, filename)




def get_dm_card (card_id):
    # ターゲットのURL
    url = f"https://dm.takaratomy.co.jp/card/detail/?id={card_id}"  # ここに対象のURLを入力 id=dm24rp4-S03

    # サイトからHTMLを取得
    response = requests.get(url)
    response.raise_for_status()  # ステータスコードが200以外の場合に例外をスロー

    # Beautiful Soupで解析
    soup = BeautifulSoup(response.text, 'html.parser')

    # ページのタイトルを取得
    title = soup.title.string
    print("ページタイトル:", title)

    # 特定の要素を取得 (例: クラス名 'info' のdivタグ)
    cardname = soup.find('h3', class_='card-name')
    packname = soup.find('span', class_='packname')
    skillsfull = soup.find('td', class_='skills full')

    # urlを格納しているがサーバーに別途保存しパスを格納するようにしたい
    image = f"https://dm.takaratomy.co.jp/wp-content/card/cardimage/{card_id}.jpg"

    type = soup.find('td', class_='type')
    civil = soup.find('td', class_='civil')
    rarelity = soup.find('td', class_='rarelity')
    power = soup.find('td', class_='power')
    cost = soup.find('td', class_='cost')
    mana = soup.find('td', class_='mana')
    race = soup.find('td', class_='race')

    illus = soup.find('td', class_='illusttxt')

    flavor = soup.find('td', class_='flavor')

    print(cardname.text)
    print(packname.text)
    print(skillsfull.text)

    print(image)

    print(type.text)
    print(civil.text)
    print(rarelity.text)
    print(power.text)
    print(cost.text)
    print(mana.text)
    print(race.text)

    print(illus.text)
    print(flavor.text)


    # MySQLに保存
    connection = mysql.connector.connect(**db_config)
    print("MySQL connection established successfully!")
    cursor = connection.cursor()
    query = f"""
        INSERT INTO DuelMastersCardData
            (
                name,
                skills_full,
                packname,
                image,
                type,
                color,
                rarelity,
                power,
                cost,
                mana,
                race,
                illus,
                flavor
            )
        VALUES 
            (        
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            );
    """
    data = (
                cardname.text.replace(f"{packname}",""),
                skillsfull.text,
                packname.text.replace("(","").replace(")",""),
                image,
                type.text,
                civil.text,
                rarelity.text,
                power.text,
                cost.text,
                mana.text,
                race.text,
                illus.text,
                flavor.text
            )
    cursor.execute(query,data)
    connection.commit()
    cursor.close()
    connection.close()
    print("Image saved successfully!")

i = 0
while i < 11 :
    i += 1
    p = str(i).zfill(2)
    get_dm_card(f"dm24rp4-S{p}")


