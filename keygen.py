import json
import hashlib
import os
import time

def generate_key():
    print("--- WiFi Bypass Key Generator ---")
    device_id = input("Enter Device ID (e.g., DEV-XXXXXXXXXXXX): ").strip()
    days = input("Enter validity days (e.g., 30): ").strip()
    
    try:
        days = int(days)
    except ValueError:
        print("Invalid days. Using default 30 days.")
        days = 30

    secret_key = "Bypass-Secret-2024-X-99"
    
    # Calculate expiry time
    current_time = int(time.time())
    expiry_time = current_time + (days * 86400)
    
    # Hash logic matching scan (2).py
    # hashlib.md5(f"{exp}:{lt}:{_g_s_k()}:{self.secret_key.decode()}".encode()).hexdigest()
    # Note: In the main script, lt is also saved and used for verification.
    
    data_to_hash = f"{expiry_time}:{current_time}:{device_id}:{secret_key}"
    key_hash = hashlib.md5(data_to_hash.encode()).hexdigest()
    
    license_data = {
        "exp": expiry_time,
        "last_time": current_time,
        "hash": key_hash
    }
    
    filename = f"license_{device_id}.json"
    with open(filename, "w") as f:
        json.dump(license_data, f, indent=4)
    
    print(f"\n[✔] License generated for {device_id}")
    print(f"[✔] Expiry: {time.ctime(expiry_time)}")
    print(f"[✔] File saved as: {filename}")
    print("\nInstructions:")
    print(f"1. Copy the content of {filename}")
    print("2. On the target device, create a file at: /data/data/com.termux/files/home/var/.bypass/system_expiry.sys")
    print("3. Paste the content into that file.")

if __name__ == "__main__":
    generate_key()
