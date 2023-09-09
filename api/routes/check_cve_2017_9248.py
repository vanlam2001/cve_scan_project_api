from fastapi import APIRouter, Depends, File, UploadFile, Form
from typing import List, Optional
import requests
from ..utils.security import get_token_authorization

router = APIRouter()

tags_cve_2017_9248 = "CVE-2017-9248"

@router.post("/api/check-vuln-cve-2017-9248", tags=[tags_cve_2017_9248])
async def check_cve_2017_9248(sites: Optional[str] = Form(None), token: str = Depends(get_token_authorization), uploaded_file: UploadFile = File(None)):
    vuln_sites = []

    # Kiểm tra nếu người nhập chuỗi hoặc upload file
    if uploaded_file:
        file_content = await uploaded_file.read()
        additional_sites = file_content.decode().splitlines()
        sites_list = additional_sites
    elif sites:
        sites_list = sites.splitlines()
    else:
        return "Chưa có dữ liệu đầu vào. Vui lòng nhập chuỗi hoặc tải lên tệp"
    
    for site in sites_list:
        vuln_site = check_site_vulnerability(site)
        vuln_sites.append(vuln_site)
    return vuln_sites

def check_site_vulnerability(site):
    try:
        paths_to_check = [
            "/DesktopModules/Admin/RadEditorProvider/DialogHandler.aspx",
            "/providers/htmleditorproviders/telerik/telerik.web.ui.dialoghandler.aspx",
            "/desktopmodules/telerikwebui/radeditorprovider/telerik.web.ui.dialoghandler.aspx",
            "/desktopmodules/dnnwerk.radeditorprovider/dialoghandler.aspx",
            "/telerik.web.ui.dialoghandler.aspx"
        ]
        for path in paths_to_check:
            url = site + path
            list = requests.get(url, verify=False, timeout=10)
            if "Loading the dialog" in list.text:
                return f"{url} -> Tìm thấy"
        return f"{site} -> Không tìm thấy"

    
    except:
        return f"{site} -> Không tìm thấy"