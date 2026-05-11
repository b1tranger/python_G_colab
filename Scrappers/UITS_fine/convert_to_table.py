import re

def convert():
    input_file = r"e:\Git_WIP\3. University repositories\CSE0613312-AI-Lab\test\results.md"
    output_file = r"e:\Git_WIP\3. University repositories\CSE0613312-AI-Lab\test\results_table.md"
    
    if not os.path.exists(input_file):
        print("Input file not found.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    table_rows = ["| Semester | Student ID | Name | Status |\n", "| :--- | :--- | :--- | :--- |\n"]
    current_semester = "Unknown"
    
    # regex to find semester headers like "# Semester 2 (04325205101001 - 04325205101250)"
    sem_pattern = re.compile(r"^# (Semester \d+)")
    # regex to find ID headers like "### ID: 04325205101015"
    id_header_pattern = re.compile(r"^### ID: (\d+)")
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for Semester
        sem_match = sem_pattern.match(line)
        if sem_match:
            current_semester = sem_match.group(1)
        
        # Check for ID block
        id_match = id_header_pattern.match(line)
        if id_match:
            sid = id_match.group(1)
            # The next few lines should be:
            # i+1: ```text
            # i+2: Name
            # i+3: ID: ...
            # i+4: Status
            try:
                name = lines[i+2].strip()
                status = lines[i+4].strip()
                table_rows.append(f"| {current_semester} | {sid} | {name} | {status} |\n")
                i += 5 # Skip the block
                continue
            except IndexError:
                pass
        
        i += 1

    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(table_rows)
    print(f"Conversion complete! Saved to {output_file}")

if __name__ == "__main__":
    import os
    convert()
