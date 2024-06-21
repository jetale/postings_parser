
urls = []
with open("lever_urls.txt", "r") as f:
    for line in f.readlines():
        if "?" in line:
            url = line.split("?")[0]+"\n"
            urls.append(url)
        else:
            urls.append(line)

with open("cleaned_lever_urls.txt", "w") as fw:
    for url in urls:
        fw.write(url)