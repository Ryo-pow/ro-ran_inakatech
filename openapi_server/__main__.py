#!/usr/bin/env python3

import connexion
from openapi_server import encoder
from openapi_server.database import db  # データベースをインポート

def main():
    app = connexion.App(__name__, specification_dir='./openapi/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('openapi.yaml',
                arguments={'title': 'Tree Management API'},
                pythonic_params=True)

    # --- ▼ データベース設定を追加 ▼ ---

    # SQLAlchemyの接続設定
    app.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trees.db'
    app.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # FlaskアプリとSQLAlchemyを接続
    db.init_app(app.app)

    # データベースのテーブルを初回作成
    with app.app.app_context():
        db.create_all()

    # --- ▲ ここまで追加 ▲ ---

    app.run(port=8080)


if __name__ == '__main__':
    main()