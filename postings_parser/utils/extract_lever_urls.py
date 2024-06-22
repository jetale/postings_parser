with open("tech_company_urls.txt", "r") as f:
    lines = f.readlines()
    for line in lines:
        if "jobs.lever.co" in line:
            line = line.replace("\n", "")
            print(line)
