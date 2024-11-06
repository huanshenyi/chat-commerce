import os
import boto3
import json
from datetime import datetime

# 外部 API 呼び出し関数を定義
import requests

def lambda_handler(event, context):
    get_parameters = event.get("parameters", [])
    keyword = get_parameters[0].get("value", "エアコン")
    data = get_cid_path(keyword)

    filtered_data = data.get("data", {}).get("list", [])

    result = extract_titles_and_paths(filtered_data)
    
    response_body = {"application/json": {"body": json.dumps(result)}}
    
    action_response = {
        "actionGroup": event.get("actionGroup", ""),
        "apiPath": event.get("apiPath", ""),
        "httpMethod": event.get("httpMethod", ""),
        "httpStatusCode": 200,
        "responseBody": response_body,
    }
    
    api_response = {"messageVersion": "1.0", "response": action_response}
    return api_response

def get_cookie():
    # secret_name = os.getenv("SECRET_NAME")
    # region_name = os.getenv("REGION_NAME")

    secret_name = "dev/chat-commerce/secret"
    region_name = "ap-northeast-1"

    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret_string = get_secret_value_response['SecretString']
        secret = json.loads(secret_string)
        return secret['COOKIE']
    except Exception as e:
        return f"クッキーの取得中にエラーが発生しました: {e}"

def get_cid_path(keyword):
    cookie = get_cookie()
    url = f"https://ec-test.nint.jp/api/genre/search-category"
    payload = {
        "data": {
         "keyword": keyword,
         "market": "rakuten",
         "product_type": "ent"
        }
    }
    headers = {
        "Cookie": f"{cookie}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"cidPathの取得中にエラーが発生しました: {e}"
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return f"{keyword}のcidPathの取得できなかった。"

def extract_titles_and_paths(data, parent_title="", result=None):
    if result is None:
        result = []
    
    for item in data:
        # 現在のアイテムからタイトルと cid_path を取得
        title = item.get("title")
        cid_path = item.get("cid_path")
        if title and cid_path:
            full_title = f"{parent_title}{title}" if parent_title else title
            result.append({"title": full_title, "cid_path": cid_path})
        
        # children が存在する場合、再帰的に処理
        children = item.get("children", [])
        if children:
            new_parent_title = f"{parent_title}{title}" if parent_title else title
            extract_titles_and_paths(children, new_parent_title, result)
    
    return result