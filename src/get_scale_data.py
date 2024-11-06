# https://ec-test.nint.jp/api/stat/get-scale-data POST
import boto3
import requests
import json
from datetime import datetime, timedelta

import requests

def lambda_handler(event, context):
    cid_path = next(
      (item["value"] for item in event["parameters"] if item["name"] == "cid_path"), ""
    )
    current_date = datetime.now()
    previous_month_date = current_date.replace(day=1) - timedelta(days=1)
    current_year_month = previous_month_date.strftime("%Y-%m")

    last_year_date = previous_month_date.replace(year=previous_month_date.year - 1)
    last_year_month = last_year_date.strftime("%Y-%m")
    date_end = next(
      (item["value"] for item in event["parameters"] if item["name"] == "date_end"), current_year_month # デフォルトは今日までの一年間
    )
    if len(date_end) == 10:
        date_obj = datetime.strptime(date_end, "%Y-%m-%d")
        date_end = date_obj.strftime("%Y-%m")

    date_start = next(
      (item["value"] for item in event["parameters"] if item["name"] == "date_start"), last_year_month
    )
    if len(date_start) == 10:
        date_obj = datetime.strptime(date_start, "%Y-%m-%d")
        date_start = date_obj.strftime("%Y-%m")
    # テスト段階はいらないかな
    # show_type = next(
    #     (item["value"] for item in event["parameters"] if item["name"] == "show_type"), "sales" # sales:売上 num:販売量
    # )
    segment_type = next(
      (item["value"] for item in event["parameters"] if item["name"] == "segment_type"), "category"  # category:ジャンル | gender:性別| maker:Top20メーカー | brand: Top20ブランド
    )

    data = get_scale_data(cid_path, date_end, date_start, segment_type)

    filtered_data = data.get("data", {})

    response_body = {"application/json": {"body": json.dumps(filtered_data)}}

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

def get_scale_data(cid_path, date_end, date_start, segment_type):
    cookie = get_cookie()
    url = "https://ec-test.nint.jp/api/stat/get-scale-data"
    payload = {
        "data": {
         "cid_path": cid_path,           
         "cutType": 0,
         "date_end": date_end,
         "date_start": date_start,
         "defaultPrice": None,
         "differ_num": 10,
         "differ_price": 0,
         "gender": "0",
         "group_type": "maker",
         "is_include_others": 0,
         "market": "rakuten",
         "other_price": 0,
         "priceEnd": None,
         "priceStart": 0,
         "price_segment_num": 10,
         "product_type": "ent",
         "segment_type": segment_type,
         "show_num": 10,
         "show_type": "sales",
         "sort_type": "total"
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
        return f"データの取得中にエラーが発生しました: {e}"
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return f"{keyword}のデータの取得できなかった。"