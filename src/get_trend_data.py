# https://ec-test.nint.jp/api/stat/get-trend-data
# show_type ジャンル情勢:sales　売れるかどうかの傾向分析
import boto3
import requests
import json
from datetime import datetime, timedelta
import requests

def lambda_handler(event, context):
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
    cid_path = next(
      (item["value"] for item in event["parameters"] if item["name"] == "cid_path"), ""
    )

    data = get_trend_data(cid_path, date_end, date_start)
    filtered_data = data.get("data", {})
    dates = filtered_data.get("dates", [])
    summary = filtered_data.get("summary", [])
    total_data = filtered_data.get("total_data", {})
    condition_sum = total_data.get("condition_sum", {})
    trend = condition_sum.get("trend", [])
    res = {
        "dates": dates,
        "summary": summary,
        "trend": trend
    }

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

def get_trend_data(cid_path, date_end, date_start):
    cookie = get_cookie()
    url = "https://ec-test.nint.jp/api/stat/get-trend-data"
    payload = {
        "data": {
         "cid_path": cid_path,
         "date_end": date_end,
         "date_start": date_start,
         "market": "rakuten",
         "product_type": "pro",
         "show_type": "sales",
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