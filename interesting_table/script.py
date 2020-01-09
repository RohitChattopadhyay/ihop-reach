import csv,html,os

journal_abbv = {}
csv_file = "./files/pmc_journal_abbreviations.csv"
reader = csv.reader(open(csv_file, 'r'))
next(reader, None)  # skip the headers
for data in reader:
    journal_abbv[html.unescape(data[0])] = html.unescape(data[1].replace(" ", "_"))

interesting_journals = []
interesting_journals_miss = []
tsv_file = "./files/interesting_journal_counts.txt"
reader =  csv.reader(open(tsv_file, 'r'), delimiter="\t")
next(reader, None)  # skip the headers
for data in reader:
    unescaped = html.unescape(data[0])
    try:
        interesting_journals.append(journal_abbv[unescaped])
    except:
        print("Not found:",unescaped)
        interesting_journals_miss.append(unescaped)
        interesting_journals.append(unescaped.replace(" ","_"))       

pmc_journals = "./files/pmc_journals/"
output_table = open('interesting_journals_table_output.csv', 'w')
interesting_journals = set(k.lower() for k in interesting_journals)
print("journal","file",sep=",",file=output_table)
for (dirpath, dirnames, filenames) in os.walk(pmc_journals):
    for file in filenames:
        txt_file = os.path.join(dirpath,file)
        reader = open(txt_file, "r")
        for line in reader:
            key = line.strip()
            if key.replace("/","").lower() in interesting_journals:
                print(key,file.replace("list_","").replace(".txt",""),file = output_table,sep=",")
