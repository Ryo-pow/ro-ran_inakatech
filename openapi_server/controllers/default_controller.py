import connexion
from typing import Dict
from typing import Tuple
from typing import Union
# from werkzeug.security import generate_password_hash の下に追記
from werkzeug.security import check_password_hash
import jwt
import datetime
from flask import current_app # Flaskアプリケーションの設定を読み込むために必要
from openapi_server.models.auth_register_post200_response import AuthRegisterPost200Response # noqa: E501
from openapi_server.models.token_response import TokenResponse # noqa: E501
from openapi_server.models.tree import Tree # noqa: E501
from openapi_server.models.trees_post_request import TreesPostRequest # noqa: E501
from openapi_server.models.trees_tree_id_lidar_delete200_response import TreesTreeIdLidarDelete200Response # noqa: E501
from openapi_server.models.trees_tree_id_lidar_post201_response import TreesTreeIdLidarPost201Response # noqa: E501
from openapi_server.models.trees_tree_id_worklogs_post_request import TreesTreeIdWorklogsPostRequest # noqa: E501
from openapi_server.models.user_login import UserLogin # noqa: E501
from openapi_server.models.user_register import UserRegister # noqa: E501
from openapi_server.models.work_log import WorkLog # noqa: E501
from openapi_server import util
# ファイルの先頭に、必要なものをインポートします
# ...インポート文...
from openapi_server.database import db, User, Tree, WorkLog as WorkLogModel
from werkzeug.security import generate_password_hash

# default_controller.py
def decode_token(token):
    """
    Connexionフレームワークがトークンを検証するために呼び出す関数
    """
    try:
        # ログイン機能で使ったものと全く同じ秘密鍵を使用
        print(f"--- [デバッグ] 検証するトークン: {token} ---")
        decoded_token = jwt.decode(token, 'your-secret-key', algorithms=['HS256'])
        print("--- [デバッグ] トークンのデコードに成功！ ---")
        return decoded_token
    except jwt.ExpiredSignatureError:
        print("--- [デバッグ] エラー: トークンの有効期限が切れています ---")
        return None
    except jwt.InvalidTokenError as e:
        # ▼ 最も重要なデバッグ情報 ▼
        print(f"--- [デバッグ] エラー: 無効なトークンです。詳細な理由: {e} ---")
        return None

def get_current_user_from_token():
    """共通のユーザー認証処理"""
    auth_header = connexion.request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None, {"message": "認証トークンが必要です"}, 401
    
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, 'your-secret-key', algorithms=['HS256'])
        return payload['sub'], None, None
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None, {"message": "無効なトークンです"}, 401

# 正しい関数が1つだけ存在する状態
def auth_register_post(body):
    user_register = body
    if connexion.request.is_json:
        user_register = UserRegister.from_dict(connexion.request.get_json())
    
    existing_user = User.query.filter_by(username=user_register.username).first()
    if existing_user:
        return {"message": "このユーザー名は既に使用されています"}, 409
    
    new_user = User(
        username=user_register.username,
        password_hash=generate_password_hash(user_register.password)
    )
    db.session.add(new_user)
    db.session.commit()
    
    return {"message": "ユーザーが正常に作成されました", "user_id": new_user.id}, 201

def auth_login_post(body): # noqa: E501
    """Login user and get JWT"""
    if connexion.request.is_json:
        user_login = UserLogin.from_dict(connexion.request.get_json())
    
    # 1. ユーザーをデータベースから探す
    user = User.query.filter_by(username=user_login.username).first()
    
    # 2. ユーザーが存在し、かつパスワードが正しいかチェック
    if not user or not check_password_hash(user.password_hash, user_login.password):
        return {"message": "ユーザー名またはパスワードが正しくありません"}, 401 # 401 Unauthorized
    
    # 3. JWT（アクセストークン）を生成する
    payload = {
        'sub': str(user.id), # トークンの主体（ユーザーID）
        'iat': datetime.datetime.utcnow(), # 発行時刻
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1) # 有効期限 (1日)
    }
    # SECRET_KEYは別途設定が必要ですが、ここでは仮の文字列を使います
    token = jwt.encode(payload, 'your-secret-key', algorithm='HS256')
    
    return {'access_token': token}

def trees_tree_id_get(tree_id):  # noqa: E501
    """Get tree details"""
    # 指定されたIDの木を検索（認証不要）
    tree = Tree.query.filter_by(id=tree_id).first()

    # もし木が見つからなければ、404エラーを返す
    if not tree:
        return {"message": "指定された木が見つかりません"}, 404

    # 見つかった木を辞書に変換して返す
    result = {
        "id": tree.id,
        "lat": tree.lat,
        "lng": tree.lng,
        "type": tree.type,
        "lidar_url": tree.lidar_url
    }
    return result

def trees_tree_id_lidar_delete(tree_id): # noqa: E501
    """Delete LiDAR file"""
    return 'do some magic!'

def trees_tree_id_lidar_head(tree_id): # noqa: E501
    """Get LiDAR file metadata"""
    return 'do some magic!'

def trees_tree_id_lidar_post(tree_id, file=None): # noqa: E501
    """Upload LiDAR file for a tree"""
    return 'do some magic!'

def trees_tree_id_worklogs_get(tree_id): # noqa: E501
    """List work logs for a tree"""
    # 1. ユーザー認証
    current_user_id, error_response, status_code = get_current_user_from_token()
    if error_response:
        return error_response, status_code
    
    # 2. 指定された木が存在し、ユーザーが所有者であることを確認
    tree = Tree.query.filter_by(id=tree_id, owner_user_id=current_user_id).first()
    if not tree:
        return {"message": "指定された木が見つからないか、アクセス権がありません"}, 404
    
    # 3. この木に関連する全ての作業日誌を取得（日付順）
    worklogs = WorkLogModel.query.filter_by(tree_id=tree_id).order_by(WorkLogModel.date.desc()).all()
    
    # 4. 作業日誌リストを辞書形式に変換
    result = []
    for worklog in worklogs:
        result.append({
            "id": worklog.id,
            "date": worklog.date.isoformat(),  # ISO形式の日付文字列に変換
            "description": worklog.description
        })
    
    return result

def trees_tree_id_worklogs_post(tree_id, body):  # noqa: E501
    """Add a new work log"""
    print(f"--- [デバッグ] 作業日誌登録開始: tree_id={tree_id} ---")
    
    # 1. ユーザー認証
    current_user_id, error_response, status_code = get_current_user_from_token()
    if error_response:
        print(f"--- [デバッグ] 認証エラー: {error_response} ---")
        return error_response, status_code
    
    print(f"--- [デバッグ] 認証成功: user_id={current_user_id} ---")
    
    # 2. リクエストボディを直接JSONから取得
    try:
        if connexion.request.is_json:
            request_data = connexion.request.get_json()
            print(f"--- [デバッグ] 受信したJSON: {request_data} ---")
        else:
            print("--- [デバッグ] JSONではないリクエストです ---")
            return {"message": "JSON形式のリクエストが必要です"}, 400
        
        # 必要なフィールドの存在確認
        if 'date' not in request_data or 'description' not in request_data:
            print("--- [デバッグ] 必要なフィールドが不足しています ---")
            return {"message": "dateとdescriptionフィールドが必要です"}, 400
        
    except Exception as e:
        print(f"--- [デバッグ] JSONパースエラー: {str(e)} ---")
        return {"message": f"リクエストの解析に失敗しました: {str(e)}"}, 400
    
    # 3. 指定された木が存在し、ユーザーが所有者であることを確認
    try:
        tree = Tree.query.filter_by(id=tree_id, owner_user_id=current_user_id).first()
        print(f"--- [デバッグ] 木の検索結果: {tree} ---")
        
        if not tree:
            print("--- [デバッグ] 指定された木が見つかりません ---")
            return {"message": "指定された木が見つからないか、アクセス権がありません"}, 404
            
    except Exception as e:
        print(f"--- [デバッグ] 木の検索でエラー: {str(e)} ---")
        return {"message": f"木の検索に失敗しました: {str(e)}"}, 500
    
    # 4. 新しい作業日誌エントリを作成
    try:
        # 日付文字列をdatetimeオブジェクトに変換
        print(f"--- [デバッグ] 日付変換前: {request_data['date']} ---")
        work_date = datetime.datetime.strptime(request_data['date'], '%Y-%m-%d').date()
        print(f"--- [デバッグ] 日付変換後: {work_date} ---")
        
        print("--- [デバッグ] WorkLogModelオブジェクト作成中 ---")
        new_worklog = WorkLogModel(
            tree_id=tree_id,
            date=work_date,
            description=request_data['description']
        )
        print(f"--- [デバッグ] WorkLogModelオブジェクト作成完了: {new_worklog} ---")
        
        print("--- [デバッグ] データベースに追加中 ---")
        db.session.add(new_worklog)
        db.session.commit()
        print("--- [デバッグ] データベースコミット完了 ---")
        
        # 5. 作成された作業日誌を返す
        result = {
            "id": new_worklog.id,
            "date": new_worklog.date.isoformat(),
            "description": new_worklog.description
        }
        print(f"--- [デバッグ] 作業日誌作成成功: {result} ---")
        
        return result, 201
        
    except ValueError as e:
        print(f"--- [デバッグ] 日付形式エラー: {str(e)} ---")
        db.session.rollback()
        return {"message": f"日付の形式が正しくありません (YYYY-MM-DD形式で入力してください): {str(e)}"}, 400
    except Exception as e:
        print(f"--- [デバッグ] 作業日誌作成エラー: {str(e)} ---")
        print(f"--- [デバッグ] エラーの詳細型: {type(e).__name__} ---")
        db.session.rollback()
        return {"message": f"作業日誌の作成に失敗しました: {str(e)}"}, 500

def trees_tree_id_worklogs_worklog_id_get(tree_id, worklog_id): # noqa: E501
    """Get work log details"""
    # 1. ユーザー認証
    current_user_id, error_response, status_code = get_current_user_from_token()
    if error_response:
        return error_response, status_code
    
    # 2. 指定された木が存在し、ユーザーが所有者であることを確認
    tree = Tree.query.filter_by(id=tree_id, owner_user_id=current_user_id).first()
    if not tree:
        return {"message": "指定された木が見つからないか、アクセス権がありません"}, 404
    
    # 3. 指定されたIDの作業日誌を取得
    worklog = WorkLogModel.query.filter_by(id=worklog_id, tree_id=tree_id).first()
    if not worklog:
        return {"message": "指定された作業日誌が見つかりません"}, 404
    
    # 4. 作業日誌の詳細を返す
    result = {
        "id": worklog.id,
        "date": worklog.date.isoformat(),
        "description": worklog.description
    }
    
    return result

def trees_get(): # noqa: E501
    """List all trees"""
    # 1. ユーザー認証（既存のコード）
    current_user_id, error_response, status_code = get_current_user_from_token()
    if error_response:
        return error_response, status_code
    
    # 2. ログイン中のユーザーが所有する木を全てデータベースから取得
    user_trees = Tree.query.filter_by(owner_user_id=current_user_id).all()
    
    # 3. 取得したTreeオブジェクトのリストを、JSONで返せる辞書のリストに変換
    result = []
    for tree in user_trees:
        result.append({
            "id": tree.id,
            "lat": tree.lat,
            "lng": tree.lng,
            "type": tree.type,
            "lidar_url": tree.lidar_url
        })
    
    return result

# 修正後の trees_post 関数
def trees_post(body, token_info): # ★ 引数に token_info が追加される
    """Create a new tree"""
    if connexion.request.is_json:
        trees_post_request = TreesPostRequest.from_dict(connexion.request.get_json())
    
    # ★ トークンは既に検証済み！デコードされた情報が token_info に入っている
    current_user_id = token_info['sub']
    
    # 新しい木オブジェクトを作成
    new_tree = Tree(
        lat=trees_post_request.lat,
        lng=trees_post_request.lng,
        type=trees_post_request.type,
        owner_user_id=current_user_id
    )
    
    # データベースに保存
    db.session.add(new_tree)
    db.session.commit()
    
    # 作成された木オブジェクトを返す
    result = {
        "id": new_tree.id,
        "lat": new_tree.lat,
        "lng": new_tree.lng,
        "type": new_tree.type,
        "lidar_url": new_tree.lidar_url
    }
    
    return result, 201
