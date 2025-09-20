import connexion
from typing import Dict
from typing import Tuple
from typing import Union
# from werkzeug.security import generate_password_hash の下に追記
from werkzeug.security import check_password_hash
import jwt
import datetime
from flask import current_app # Flaskアプリケーションの設定を読み込むために必要

from openapi_server.models.auth_register_post200_response import AuthRegisterPost200Response  # noqa: E501
from openapi_server.models.token_response import TokenResponse  # noqa: E501
from openapi_server.models.tree import Tree  # noqa: E501
from openapi_server.models.trees_post_request import TreesPostRequest  # noqa: E501
from openapi_server.models.trees_tree_id_lidar_delete200_response import TreesTreeIdLidarDelete200Response  # noqa: E501
from openapi_server.models.trees_tree_id_lidar_post201_response import TreesTreeIdLidarPost201Response  # noqa: E501
from openapi_server.models.trees_tree_id_worklogs_post_request import TreesTreeIdWorklogsPostRequest  # noqa: E501
from openapi_server.models.user_login import UserLogin  # noqa: E501
from openapi_server.models.user_register import UserRegister  # noqa: E501
from openapi_server.models.work_log import WorkLog  # noqa: E501
from openapi_server import util
# ファイルの先頭に、必要なものをインポートします
# ...インポート文...
from openapi_server.database import db, User, Tree
from werkzeug.security import generate_password_hash

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

# ...以降の関数（trees_get, trees_postなど）...
def auth_login_post(body):  # noqa: E501
    """Login user and get JWT
    """
    if connexion.request.is_json:
        user_login = UserLogin.from_dict(connexion.request.get_json())
    
    # 1. ユーザーをデータベースから探す
    user = User.query.filter_by(username=user_login.username).first()

    # 2. ユーザーが存在し、かつパスワードが正しいかチェック
    if not user or not check_password_hash(user.password_hash, user_login.password):
        return {"message": "ユーザー名またはパスワードが正しくありません"}, 401 # 401 Unauthorized

    # 3. JWT（アクセストークン）を生成する
    payload = {
        'sub': user.id, # トークンの主体（ユーザーID）
        'iat': datetime.datetime.utcnow(), # 発行時刻
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1) # 有効期限 (1日)
    }
    
    # SECRET_KEYは別途設定が必要ですが、ここでは仮の文字列を使います
    token = jwt.encode(payload, 'your-secret-key', algorithm='HS256')

    return {'access_token': token}

def trees_tree_id_get(tree_id):  # noqa: E501
    """Get tree details
    """
    # 1. JWTからユーザーを特定
    auth_header = connexion.request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return {"message": "認証トークンが必要です"}, 401
    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, 'your-secret-key', algorithms=['HS256'])
        current_user_id = payload['sub']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return {"message": "無効なトークンです"}, 401

    # 2. 指定されたIDを持ち、かつログイン中のユーザーが所有する木を検索
    tree = Tree.query.filter_by(id=tree_id, owner_user_id=current_user_id).first()

    # 3. もし木が見つからなければ、404エラーを返す
    if not tree:
        return {"message": "指定された木が見つからないか、アクセス権がありません"}, 404

    # 4. 見つかった木を辞書に変換して返す
    result = {
        "id": tree.id,
        "lat": tree.lat,
        "lng": tree.lng,
        "type": tree.type,
        "lidar_url": tree.lidar_url
    }

    return result

def trees_tree_id_lidar_delete(tree_id):  # noqa: E501
    """Delete LiDAR file

     # noqa: E501

    :param tree_id: 
    :type tree_id: int

    :rtype: Union[TreesTreeIdLidarDelete200Response, Tuple[TreesTreeIdLidarDelete200Response, int], Tuple[TreesTreeIdLidarDelete200Response, int, Dict[str, str]]
    """
    return 'do some magic!'


def trees_tree_id_lidar_head(tree_id):  # noqa: E501
    """Get LiDAR file metadata

     # noqa: E501

    :param tree_id: 
    :type tree_id: int

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def trees_tree_id_lidar_post(tree_id, file=None):  # noqa: E501
    """Upload LiDAR file for a tree

     # noqa: E501

    :param tree_id: 
    :type tree_id: int
    :param file: 
    :type file: str

    :rtype: Union[TreesTreeIdLidarPost201Response, Tuple[TreesTreeIdLidarPost201Response, int], Tuple[TreesTreeIdLidarPost201Response, int, Dict[str, str]]
    """
    return 'do some magic!'


def trees_tree_id_worklogs_get(tree_id):  # noqa: E501
    """List work logs for a tree

     # noqa: E501

    :param tree_id: 
    :type tree_id: int

    :rtype: Union[List[WorkLog], Tuple[List[WorkLog], int], Tuple[List[WorkLog], int, Dict[str, str]]
    """
    return 'do some magic!'


def trees_tree_id_worklogs_post(tree_id, body):  # noqa: E501
    """Add a new work log

     # noqa: E501

    :param tree_id: 
    :type tree_id: int
    :param trees_tree_id_worklogs_post_request: 
    :type trees_tree_id_worklogs_post_request: dict | bytes

    :rtype: Union[WorkLog, Tuple[WorkLog, int], Tuple[WorkLog, int, Dict[str, str]]
    """
    trees_tree_id_worklogs_post_request = body
    if connexion.request.is_json:
        trees_tree_id_worklogs_post_request = TreesTreeIdWorklogsPostRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def trees_tree_id_worklogs_worklog_id_get(tree_id, worklog_id):  # noqa: E501
    """Get work log details

     # noqa: E501

    :param tree_id: 
    :type tree_id: int
    :param worklog_id: 
    :type worklog_id: int

    :rtype: Union[WorkLog, Tuple[WorkLog, int], Tuple[WorkLog, int, Dict[str, str]]
    """
    return 'do some magic!'

def trees_get():  # noqa: E501
    """List all trees
    """
    # 1. ヘッダーからJWTを取得し、ユーザーを特定
    auth_header = connexion.request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return {"message": "認証トークンが必要です"}, 401
    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, 'your-secret-key', algorithms=['HS256'])
        current_user_id = payload['sub']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return {"message": "無効なトークンです"}, 401

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

def trees_post(body):  # noqa: E501
    """Create a new tree
    """
    if connexion.request.is_json:
        trees_post_request = TreesPostRequest.from_dict(connexion.request.get_json())
    
    # 1. ヘッダーからJWTを取得
    auth_header = connexion.request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return {"message": "認証トークンが必要です"}, 401

    token = auth_header.split(" ")[1]

    try:
        # 2. JWTをデコードしてユーザーIDを取得
        # 'your-secret-key'はログイン機能で使ったものと同じキーにします
        payload = jwt.decode(token, 'your-secret-key', algorithms=['HS256'])
        current_user_id = payload['sub']
    except jwt.ExpiredSignatureError:
        return {"message": "トークンの有効期限が切れています"}, 401
    except jwt.InvalidTokenError:
        return {"message": "無効なトークンです"}, 401

    # 3. 新しい木オブジェクトを作成
    new_tree = Tree(
        lat=trees_post_request.lat,
        lng=trees_post_request.lng,
        type=trees_post_request.type,
        owner_user_id=current_user_id  # JWTから取得したIDを所有者として設定
    )

    # 4. データベースに保存
    db.session.add(new_tree)
    db.session.commit()

    # 5. 作成された木オブジェクトを返す
    # 注意：Treeモデルのオブジェクトを直接返せないので、辞書に変換します
    result = {
        "id": new_tree.id,
        "lat": new_tree.lat,
        "lng": new_tree.lng,
        "type": new_tree.type,
        "lidar_url": new_tree.lidar_url
    }
    
    return result, 201