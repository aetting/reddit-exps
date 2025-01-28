phrases = set()

with open("temp_keywords.txt") as f:
    for line in f:
        line = line.strip().strip(",").strip(".").replace('"',"").lower()
        phrases.add(line)
    print(list(phrases))
        
