import os
import sys
import json
import hashlib
import subprocess
import urllib.request

# --- CONFIGURATION ---
URL = "https://mrinmoybiswasu.github.io/performance-and-attendance/"
DATA_URL = "https://mrinmoybiswasu.github.io/performance-and-attendance/data.enc"
OUTPUT_FILE = "results.md"
FINE_PASS = "UITS-CSE-Spring2026-Fine"

# Semester ranges for Autumn 2026
# Format: (Semester_Name, Start_ID, End_ID)
SEMESTER_RANGES = [
    ("Semester 1", "04326205101001", "04326205101250"),
    ("Semester 2", "04326105101001", "04326105101250"),
    ("Semester 3", "04325205101001", "04325205101250"),
    ("Semester 4", "04325105101001", "04325105101250"),
    ("Semester 5", "04324205101001", "04324205101250"),
    ("Semester 5", "04324205191001", "04324205191050"),
    ("Semester 6", "0432410005101001", "0432410005101250"),
    ("Semester 7", "0432320005101001", "0432320005101250"),
    ("Semester 8", "0432310005101001", "0432310005101250"),
    ("Retake / Ex-Batch", "0432220005101001", "0432220005101250"),
]

def generate_id_range(start_id_str, end_id_str):
    """Generates a list of IDs from start to end, preserving the original length."""
    try:
        length = len(start_id_str)
        start = int(start_id_str)
        end = int(end_id_str)
        if start > end:
            return []
        return [str(i).zfill(length) for i in range(start, end + 1)]
    except ValueError:
        return []

def decrypt_with_cryptography(b64_data, passphrase):
    """Decrypts data using python cryptography package if available."""
    import base64
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    raw = base64.b64decode(b64_data)
    key = hashlib.sha256(passphrase.encode("utf-8")).digest()
    iv = raw[:12]
    ciphertext = raw[12:]
    aesgcm = AESGCM(key)
    plain = aesgcm.decrypt(iv, ciphertext, None)
    return json.loads(plain.decode("utf-8"))

def decrypt_with_node(b64_data_file, passphrase):
    """Decrypts data using Node.js WebCrypto (native on Windows/Node)."""
    node_script = """
    const fs = require('fs');
    const crypto = require('crypto').webcrypto;
    const pass = process.argv[1];
    const filePath = process.argv[2];

    async function deriveKey(p) {
        const raw = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(p));
        return crypto.subtle.importKey('raw', raw, {name:'AES-GCM'}, false, ['decrypt']);
    }

    async function decrypt(b64, p) {
        const raw = new Uint8Array(Buffer.from(b64, 'base64'));
        const key = await deriveKey(p);
        const plain = await crypto.subtle.decrypt({name:'AES-GCM', iv: raw.slice(0, 12)}, key, raw.slice(12));
        return JSON.parse(new TextDecoder().decode(plain));
    }

    (async () => {
        const b64 = fs.readFileSync(filePath, 'utf8').trim();
        const db = await decrypt(b64, pass);
        process.stdout.write(JSON.stringify(db));
    })();
    """
    res = subprocess.run(["node", "-e", node_script, passphrase, b64_data_file], capture_output=True, text=True, check=True)
    return json.loads(res.stdout)

def fetch_and_decrypt_db():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_enc_path = os.path.join(base_dir, "data.enc")

    if not os.path.exists(data_enc_path):
        print(f"[*] Downloading {DATA_URL}...")
        try:
            urllib.request.urlretrieve(DATA_URL, data_enc_path)
            print("[+] Download complete.")
        except Exception as e:
            print(f"[!] Network download error: {e}")
            if not os.path.exists(data_enc_path):
                raise

    # Attempt decryption via Python cryptography, fallback to Node
    try:
        with open(data_enc_path, "r", encoding="utf-8") as f:
            b64_content = f.read().strip()
        db = decrypt_with_cryptography(b64_content, FINE_PASS)
        print("[+] Decrypted using Python cryptography.")
        return db
    except ImportError:
        pass

    try:
        db = decrypt_with_node(data_enc_path, FINE_PASS)
        print("[+] Decrypted using Node.js WebCrypto.")
        return db
    except Exception as e:
        print(f"[!] Node.js decryption failed: {e}")
        raise RuntimeError("Could not decrypt data. Please ensure Node.js is installed or install the 'cryptography' Python package.")

def scrape_attendance():
    print(f"[*] Scraping attendance records from {URL}...")
    db = fetch_and_decrypt_db()
    print(f"[+] Loaded {len(db)} student records from database.")

    all_results = ["| Semester | Student ID | Name | Status |\n", "| :--- | :--- | :--- | :--- |\n"]
    matched_ids = set()

    for sem_name, start_id, end_id in SEMESTER_RANGES:
        if start_id == "0":
            continue

        semester_ids = generate_id_range(start_id, end_id)
        found_in_sem = 0

        for sid in semester_ids:
            if sid in db:
                matched_ids.add(sid)
                found_in_sem += 1
                s = db[sid]
                status = "⚠ Under-Attendance" if s.get("has_under_attendance") else "✓ Attendance OK"
                name = s.get("name", "N/A")
                all_results.append(f"| {sem_name} | {sid} | {name} | {status} |\n")

        print(f"[+] {sem_name} ({start_id}..): {found_in_sem} records found")

    # Include any remaining older batches under Retake / Ex-Batch
    remaining_ids = sorted([k for k in db.keys() if k not in matched_ids])
    if remaining_ids:
        print(f"[+] Retake / Older batches: {len(remaining_ids)} records found")
        for sid in remaining_ids:
            s = db[sid]
            status = "⚠ Under-Attendance" if s.get("has_under_attendance") else "✓ Attendance OK"
            name = s.get("name", "N/A")
            all_results.append(f"| Retake / Ex-Batch | {sid} | {name} | {status} |\n")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, OUTPUT_FILE)
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(all_results)

    print(f"\n[!] Done! Total records written: {len(all_results) - 2}")
    print(f"[!] Results saved to: {output_path}")

if __name__ == "__main__":
    scrape_attendance()
