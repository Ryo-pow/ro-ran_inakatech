#!/usr/bin/env python3
import connexion
import pathlib  # ★ 1. ファイルパスを扱うためのライブラリをインポート
from openapi_server import encoder
from openapi_server.database import db

def main():
    # ★ 2. このファイルがある場所を基準に、設計図の絶対パスを特定する
    spec_dir = pathlib.Path(__file__).parent / "openapi"

    app = connexion.App(__name__, specification_dir=spec_dir)
    app.app.json_encoder = encoder.JSONEncoder

    # ★ 3. ファイル名を直接指定
    app.add_api('openapi.yaml',
                arguments={'title': 'Tree Management API'},
                pythonic_params=True)

    # --- データベース設定 ---
    app.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trees.db'
    app.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app.app)
    with app.app.app_context():
        db.create_all()
    # --- ここまで ---

    app.run(port=8080, host='0.0.0.0')

if __name__ == '__main__':
    main()