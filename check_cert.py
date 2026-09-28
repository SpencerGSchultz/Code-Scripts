# check_cert.py
# Usage: python check_cert.py <PEM_PATH> <URL>
# Example: python check_cert.py privatei_chain.pem https://privatei.burgiss.com/lpinvestments?page=1

import sys
import requests

def main():
    if len(sys.argv) != 3:
        print("Usage: python check_cert.py <PEM_PATH> <URL>")
        sys.exit(1)

    pem_path = sys.argv[1]
    url = sys.argv[2]

    try:
        print(f"Testing {url} using CA bundle: {pem_path}")
        r = requests.get(url, verify=pem_path, timeout=15)
        print("✅ Connection OK — Status:", r.status_code)
        print("Response length:", len(r.content))
    except requests.exceptions.SSLError as e:
        print("❌ SSL certificate verification failed:", e)
    except requests.exceptions.ConnectionError as e:
        print("❌ Connection error:", e)
    except Exception as e:
        print("❌ Other error:", e)

if __name__ == "__main__":
    main()
