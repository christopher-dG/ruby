import os

import requests

API = "https://api.netlify.com/api/v1"
TOKEN = os.environ["NETLIFY_TOKEN"]
DOMAIN = "cdg.dev"
WILDCARD = f"*.{DOMAIN}"


def netlify_api(path, method="GET", json=None):
    resp = requests.request(
        method,
        API + path,
        headers={"Authorization": f"Bearer {TOKEN}"},
        json=json,
    )
    resp.raise_for_status()
    return resp


def netlify_get(path):
    return netlify_api(path).json()


def delete_record(zone, record):
    return netlify_api(f"/dns_zones/{zone}/dns_records/{record}", method="DELETE")


def create_record(zone, type, hostname, value):
    payload = {"type": type, "hostname": hostname, "value": value}
    return netlify_api(f"/dns_zones/{zone}/dns_records", method="POST", json=payload)


def find(xs, key, val):
    for x in xs:
        if x[key] == val:
            return x
    raise ValueError("No such value")


def update_record(zone, ip):
    records = netlify_get(f"/dns_zones/{zone}/dns_records")
    print(f"Searching {len(records)} records")
    print(f"IP: {ip}")
    good_record_exists = False
    for record in records:
        if record["type"] == "A" and record["hostname"] == WILDCARD:
            if record["value"] == ip:
                print("Existing record has correct value")
                good_record_exists = True
            else:
                print("Deleting outdated record")
                delete_record(zone, record["id"])
    if not good_record_exists:
        print("Creating record")
        create_record(zone, "A", WILDCARD, ip)


if __name__ == "__main__":
    site = find(netlify_get("/sites"), "custom_domain", DOMAIN)["id"]
    print(f"Site ID: {site}")
    zone = find(netlify_get(f"/sites/{site}/dns"), "name", DOMAIN)["id"]
    print(f"Zone ID: {zone}")
    ip = requests.get("https://httpbin.org/ip").json()["origin"]
    update_record(zone, ip)
