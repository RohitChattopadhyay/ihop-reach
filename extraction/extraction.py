import argparse,os,time,sys
import pandas as pd

def terminalCommand(cmd):
    os.system(cmd)

def progress(count, total, status='', end='\r\n'):
    terminalCommand('clear') 
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s%s' % (bar, percents, '%', status,end))
    sys.stdout.flush()

# initiate the cli argument parser
parser = argparse.ArgumentParser()

# add long and short argument
parser.add_argument("--path", "-p", help="Path to list of journals")

# read arguments from the command line
args = parser.parse_args()

if os.name == 'nt': 
    # For Windows
    print("Operating System not supported, try any UNIX based OS")
    quit()

if args.path:
    try:
        df = pd.read_csv(args.path)
    except FileNotFoundError: 
        print("Invalid path provided or File does not exits.")
    
    files = list(df.file.unique())
    try:
        r_log = pd.read_csv("extraction_restart.log",header=None)
        for i in r_log[0].tolist():
            if i in files:
                files.remove(i)
    except:
        print("Extraction log not found")

    l = len(files)
    f_counter = 0
    if l==0:
        print("All files processed, please remove extraction_restart.log and try again.")
        quit()

    terminalCommand("mkdir papers")

    progress(f_counter,l, status = 'Starting')    
    for file in files:
        progress(f_counter,l, status = file)    
        journals = df.journal[df.file==file].tolist()
        with open('temp_journals_list', 'w') as f:
            for journal in journals:
                f.write("%s\n" % journal)
        link = "ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/" + file

        print("Downloading\t\t:\t",file)
        terminalCommand("curl -o ./source.tar.gz \"%s\"" % link)

        print("Extracting\t\t:\t",file)
        terminalCommand("tar -xzf ./source.tar.gz -C ./papers/ -T ./temp_journals_list")
        
        with open("extraction_restart.log", "a") as log:
            log.write(file+"\n")        
        f_counter = f_counter + 1 
        print("Extraction Complete\t:\t",file)
        terminalCommand("rm source.tar.gz temp_journals_list")
        time.sleep(.5)
    progress(1,1, status = "Complete")    

else:
    print("Argument path missing, use argument -h for help.")