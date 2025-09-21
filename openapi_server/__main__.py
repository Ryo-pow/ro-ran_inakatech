#!/usr/bin/env python3
import connexion
import pathlib  # ★ 1. ファイルパスを扱うためのライブラリをインポート
from flask import request, make_response
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

    # --- CORS 設定 ---
    @app.app.after_request
    def add_cors_headers(response):
        # 必要に応じて許可オリジンを限定する
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        return response

    @app.app.before_request
    def handle_preflight():
        # ブラウザのプリフライト(OPTIONS)に即時応答
        if request.method == 'OPTIONS':
            resp = make_response('', 204)
            resp.headers['Access-Control-Allow-Origin'] = '*'
            req_headers = request.headers.get('Access-Control-Request-Headers')
            resp.headers['Access-Control-Allow-Headers'] = req_headers or 'Authorization, Content-Type'
            req_method = request.headers.get('Access-Control-Request-Method')
            resp.headers['Access-Control-Allow-Methods'] = (req_method + ', OPTIONS') if req_method else 'GET, POST, PUT, DELETE, OPTIONS'
            return resp
    # --- CORS 設定ここまで ---

    app.run(port=8080, host='0.0.0.0')

if __name__ == '__main__':
    main()
