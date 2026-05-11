import asyncio
import os
from playwright.async_api import async_playwright

# --- CONFIGURATION ---
URL = "https://mrinmoybiswasu.github.io/performance-and-attendance/"
OUTPUT_FILE = "results.md"

# Specify the 8 semester ranges here
# Format: (Semester_Name, Start_ID, End_ID)
SEMESTER_RANGES = [
    ("Semester 1", "04326105101001", "04326105101250")
    # ,
    # ("Semester 2", "04325205101001", "04325205101250"), 
    # ("Semester 3", "04325105101001", "04325105101250"),
    # ("Semester 4", "04324205101002", "04324205101250"),
    # ("Semester 5", "0432410005101001", "0432410005101250"),
    # ("Semester 6", "0432320005101001", "0432320005101250"),
    # ("Semester 7", "0432310005101001", "0432310005101250"),
    # ("Semester 8", "0432220005101001", "0432220005101250"),
]

def generate_id_range(start_id_str, end_id_str):
    """Generates a list of IDs from start to end, preserving the original length."""
    try:
        length = len(start_id_str)
        start = int(start_id_str)
        end = int(end_id_str)
        if start > end:
            return []
        # Return as padded strings matching the original input length
        return [str(i).zfill(length) for i in range(start, end + 1)]
    except ValueError:
        return []

async def scrape_attendance():
    async with async_playwright() as p:
        print(f"[*] Launching headless browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print(f"[*] Navigating to {URL}...")
        try:
            await page.goto(URL, wait_until="networkidle")
        except Exception as e:
            print(f"[!] Error loading page: {e}")
            await browser.close()
            return

        # Initialize table with headers
        all_results = ["| Semester | Student ID | Name | Status |\n", "| :--- | :--- | :--- | :--- |\n"]

        for sem_name, start_id, end_id in SEMESTER_RANGES:
            if start_id == "0": continue 
            
            print(f"\n[>>>] Processing {sem_name}: {start_id} to {end_id}")
            semester_ids = generate_id_range(start_id, end_id)
            
            if not semester_ids:
                print(f"[!] Invalid range for {sem_name}")
                continue

            for sid in semester_ids:
                print(f"[*] Querying ID: {sid}...")
                
                try:
                    await page.fill("#sid-input", "")
                    await page.fill("#sid-input", sid)
                    await page.press("#sid-input", "Enter")
                    
                    await page.wait_for_selector("#loading", state="hidden", timeout=10000)
                    result_found = await page.wait_for_selector(".student-meta, .alert-error", timeout=5000)
                    
                    class_list = await result_found.evaluate("el => el.className")
                    
                    if "student-meta" in class_list:
                        # Extract and parse content
                        content = await page.inner_text(".student-meta")
                        lines = [line.strip() for line in content.split('\n') if line.strip()]
                        
                        # Expected structure: Name, ID, Status
                        name = lines[0] if len(lines) > 0 else "N/A"
                        status = lines[2] if len(lines) > 2 else "N/A"
                        
                        # Append as a table row
                        all_results.append(f"| {sem_name} | {sid} | {name} | {status} |\n")
                        print(f"[+] Success: {sid}")
                    else:
                        print(f"[-] No record for {sid}")
                
                except Exception as e:
                    print(f"[!] Timeout/Error for {sid}")

                await asyncio.sleep(0.5)

        # Write to file
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.writelines(all_results)

        print(f"\n[!] Done! Results saved to: {os.path.abspath(OUTPUT_FILE)}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_attendance())
