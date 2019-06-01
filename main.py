import csv, time, sys, argparse, win32api, win32net, traceback, connector, getpass, subprocess, wmi, os, yaml
parser = argparse.ArgumentParser(usage = '\n Remote Artifact Analysis and Retrieval\n  -t -- [Target Host-Name or IP Address (Only One)]\n -c -- UserName to Connect Via (Alt Account)\n  -u -- Target User Name to Inspect')
parser.add_argument("-t", "--target", help='Specify Target Host Name or IP Address', required = True) #Target machine
parser.add_argument("-c", "--credential", help='Specify UID to Connect VIA', required = True) #Credential/UserName for Access
parser.add_argument("-u", "--user_target", help='Specify UID to Target', required = True) #Target User for Analysis
parser.add_argument("-a", "--admin", help='Use if running in alt/administrator cmdline', required = False, action="store_true") #If admin, can use winreg on local/direct WMI, else need to authenticate and perform on remote.
args = parser.parse_args()
target = args.target
elevated_username = args.credential
user_target = args.user_target
admin_priv = args.admin
artifact_file="artifacts.csv" #Input Artifact File in format "TYPE, NAME, ; separated VALUES, DOCUMENTATION
yaml_data_folder = "data" #Name of folder storing .yaml artifact signatures
global type_dict, values_dict, doc_dict, base_user_dir, user_appdata_dir, user_local_appdata_dir, user_roaming_appdata_dir
domain = "X"

def main():#Because every tool has ASCII art, right?
    print("########################################\n")
    print(" _    _  ___  ____________ ")
    print("| |  | |/ _ \ | ___ \  _  \\")
    print("| |  | / /_\ \| |_/ / | | |")
    print("| |/\| |  _  ||    /| | | |")
    print("\  /\  / | | || |\ \| |/ / ")
    print(" \/  \/\_| |_/\_| \_|___/  ")
    print("########################################\n")
    print("Windows Artifact Retrieval and Discovery\n")
    print("Joe Avanzato , github.com/joeavanzato\n")
    print("########################################\n")

    read_yaml_data()


    #Temporarily commenting out main functions
    #parse_artifacts() #Read the Input File (TYPE, NAME, VALUES(; sep.), DOCUMENTATION
    #separate_into_named_lists() #Separate the gathered data into various lists
    #establish_connection() #Prepare Connection to Remote HOst
    #test_connection() #Verify working connection with ipconfig
    #parse_and_pass() #Check artifact type and pass to helper functions for cmd execution

def read_yaml_data():
    yaml_files = [f for f in os.listdir(yaml_data_folder) if os.path.isfile(os.path.join(yaml_data_folder, f))]
    with open('artifacts_all.csv', 'w', newline='') as a:
        #writer = csv.writer(a, delimiter=',')
        for file in yaml_files:
            with open(yaml_data_folder+"\\"+file) as f:
                for item in yaml.load_all(f):
                    source_data = item.get("sources")
                    for data_feed in source_data:
                        print("")
                        if "Windows" in str(item.get("supported_os")):
                            #print(item.get("name"))
                            name = item.get("name")
                            #print(item.get("doc"))
                            documentation = item.get("doc")
                            #print(data_feed.get("type"))
                            art_type = data_feed.get("type")
                            if art_type == "FILE":
                                attributes = data_feed.get("attributes")
                                #print(attributes)
                                paths = attributes.get("paths")
                                path_string = ""
                                len(paths)
                                x = 0
                                for value in paths:
                                    print(value)
                                    if x == 0: 
                                        path_string = value
                                    else:
                                        path_string = path_string + ";" + value
                                    x = x + 1
                                row = art_type+","+name+","+path_string+","+documentation.replace(",","-").replace("\n","").replace("\r","")+"\n"
                                a.write(row)

                            #ADD STATEMENTS FOR OTHER ARTIFACT TYPES

                            #print(item.get("sources"))
                            #print(item.get("supported_os"))
                            #print(data_feed)
                            #row = art_type+","+name+","+"X"+","+documentation.replace(",","-").replace("\n","").replace("\r","")+"\n"
                            #a.write(row)
                        else:
                            pass


def establish_connection(): #Setup WMI Connection, Get SID, UserPath and default WINDIR
    global rem_con, user_sid, user_path, system_root, base_user_dir, user_appdata_dir, user_local_appdata_dir, user_roaming_appdata_dir, win_dir, win_def
    print("Building Remote Connection..\n")
    if admin_priv == False:
        password = getpass.getpass(prompt="Password for "+elevated_username+":")
        rem_con = connector.connector(target, elevated_username, password, user_target, domain)
    else:
        rem_con = connector.connector(target, elevated_username, password, user_target, domain)
    try:
        rem_con.create_session()
    except:
        print("ERROR Initializing WMI Connection..does your credential have Remote Access?")
        print(traceback.print_exc(sys.exc_info()))
        exit(0)
    try:#Prepare some paths for replacement in artifacts
        user_sid, user_path = rem_con.get_sid()
        system_root = user_path[0]
        base_user_dir = system_root+":\\Users\\" + user_target
        user_appdata_dir = base_user_dir+"AppData"
        user_local_appdata_dir = user_appdata_dir+"\\"+"Local"
        user_roaming_appdata_dir = user_appdata_dir+"\\"+"Roaming"
        win_def = 0 
    except:#NEED SID for real functionality
        print("ERROR Getting Target User SID..")
        print(traceback.print_exc(sys.exc_info()))
        exit(0)
    try:
        win_dir = rem_con.get_windir()
        print("Found WINDIR at "+win_dir)
    except:
        win_def = 1
        print("Failed Finding default WINDIR, using "+system_root+":\Windows")
    rem_con.write_default()

def test_connection():#Run basic command, make sure nothing breaks, could probably use return_value != 0 also
    print("\nVerifying Connectivity..")
    command = 'ipconfig /all'
    try:
        rem_con.execute(command, "ipconfig", 0, ".txt")
    except:
        print("ERROR Executing Command..Does the User Account lack WMI permissions?")
        print(traceback.print_exc(sys.exc_info()))
        exit(0)

def replace_values(item):#Replace placeholder strings in artifacts with gathered data -> check for other necessary replacements
    if "%%users.userprofile%%" in item:
        item = item.replace("%%users.userprofile%%", base_user_dir)
    if "%%users.sid%%" in item:
        item = item.replace("%%users.sid%%", user_sid)
    if "%%users.username%%" in item:
        item = item.replace("%%users.username%%", user_target)
    if "%%users.temp%%" in item:
        item = item.replace("%%users.temp%%", user_local_appdata_dir+"\Temp")
    if "%%users.localappdata%%" in item:
        item = item.replace("%%users.localappdata%%", user_local_appdata_dir)
    if "%%users.appdata%%" in item:
        item = item.replace("%%users.appdata%%", user_appdata_dir)
    if "%%environ_systemroot%%" in item:
        item = item.replace("%%environ_systemroot%%", system_root+":\Windows")
    if "%%environ_systemdrive%%" in item:
        item = item.replace("%%environ_systemdrive%%", system_root)
    if ("%%environ_windir%%" in item) and (win_def == 0):
        item = item.replace("%%environ_windir%%", win_dir)
    elif ("%%environ_windir%%" in item) and (win_def == 1):
        item = item.replace("%%environ_windir%%", system_root+":\Windows")
    if "%%environ_allusersappdata%%" in item:
        item = item.replace("%%environ_allusersappdata%%", system_root+":\ProgramData")
    if "%%environ_programfiles%%" in item:
        item = item.replace("%%environ_programfiles%%", system_root+":\Program Files")
    if "%%environ_programfilesx86%%" in item:
        item = item.replace("%%environ_programfilesx86%%", system_root+":\Program Files (x86)")
    return item

def split_items(values): #Split REGV into key:value pair -> think about building straight or still using CSV
    item_dict = {}
    item_list = values.split(";")
    x = 0
    len_list = len(item_list)
    #print(str(len_list))
    while x < len(item_list):
        #print(str(x))
        item_dict[item_list[x]] = item_list[x+1]
        #print(item_list[x])
        #print(item_list[x+1])
        x = x + 2
        #print(str(x))
    return item_dict

def parse_and_pass():#Separate values in individual artifact types and send to handler function, TO DO REGK
    for item in directories:
        #print(item)
        artifact_name = item
        value_raw = values_dict.get(item)
        #print(value_raw)
        item_list = replace_values(value_raw)
        items_list = item_list.split(";")
        x = 0
        for item in items_list:
            check_dir_contents(item, artifact_name, x)
            x = x + 1

    for item in registry_values:
        #print(item)
        artifact_name = item
        value_raw = values_dict.get(item)
        #print(value_raw)
        temp_values_dict = split_items(value_raw)
        print("\nArtifact Name: " + artifact_name)
        x = 0 
        for key, value in temp_values_dict.items():
            try:
                key = replace_values(key)
                reg_key = key
                reg_value = value
                check_reg_values(reg_key, reg_value, artifact_name, x)
                x = x + 1
            except:
                print("Error Reading Key:Value "+reg_key+":"+reg_value)
                x = x + 1

    for item in files:
        artifact_name = item
        value_raw = values_dict.get(item)
        item_list = replace_values(value_raw)
        file_list = item_list.split(";")
        print("\nArtifact Name: " + artifact_name)
        x = 0
        for file in file_list:
            try:
                gather_file(file, artifact_name, x)
                x = x + 1
            except:
                print("ERROR copying file '"+file+"' in artifact "+artifact_name+"'")
                x = x + 1

def parse_artifacts():
    global type_dict, values_dict, doc_dict, artifact_count
    type_dict = {}
    values_dict = {}
    doc_dict = {}
    print("Loading Artifact Data from 'artifacts.csv'..")
    with open(artifact_file, 'r') as f:
        error_count = 0
        line_count = 0
        for line in f:
            try:
                #print(line)
                atype, name, values, doc = line.split(",")
                atype = atype.replace("\"", "").strip()
                name = name.replace("\"", "").strip()
                values=values.replace("\"", "").strip()
                doc=doc.replace("\"", "").strip()
                type_dict[name] = atype
                values_dict[name] = values
                doc_dict[name] = doc
                #print(atype+" "+name+" "+values+" "+doc)
                line_count = line_count + 1
            except:
                print(traceback.print_exc(sys.exc_info()))
                print("Error Loading Data on Line "+str(line_count))
                error_count = error_count + 1
                pass

    artifact_count = 0
    for key in doc_dict.items():
        artifact_count = artifact_count + 1
    print("Loaded Types, Names, Values and Documentation with "+str(error_count)+" Errors..")
    print("Total of "+str(artifact_count)+" separate artifact definitions found in database..")

def separate_into_named_lists(): #Add lists for other types, etc
    print("Separating Data..\n")
    global registry_keys, registry_values, files, commands, directories
    registry_keys = []
    registry_values = []
    files = []
    commands = []
    directories = []

    for key, value in type_dict.items(): #Rename according to proper artifact names, add other artifact types
        if value == "REGK":
            registry_keys.append(key)
        elif value == "REGV":
            registry_values.append(key)
        elif value == "FILE":
            files.append(key)
        elif value == "CMD":
            commands.append(key)
        elif value == "DIR":
            directories.append(key)
    count_reg_keys = 0
    count_reg_values = 0
    count_files = 0
    count_commands = 0
    count_directories = 0
    for item in registry_keys:
        count_reg_keys = count_reg_keys + 1
    for item in registry_values:
        count_reg_values = count_reg_values + 1
    for item in files:
        count_files = count_files + 1
    for item in commands:
        count_commands = count_commands + 1
    for item in directories:
        count_directories = count_directories + 1
    print("REGISTRY KEY ENTRIES : "+str(count_reg_keys)) #Add print for other types
    print("REGISTRY VALUE ENTRIES : "+str(count_reg_values))
    print("FILE ENTRIES : "+str(count_files))
    print("COMMAND ENTRIES : "+str(count_commands))
    print("DIRECTORY ENTRIES : "+str(count_directories))


def check_dir_contents(directory, artifact_name, iteration):#Send directory path to WMI Session for 'dir' execution
    print("\nArtifact Name: "+artifact_name)
    print("Examining Contents of Directory : " + directory)
    if "*" in directory:
        directory = directory.replace("*","")
        command = "dir /s "+directory
    else:
        command = "dir "+directory
    rem_con.execute(command, artifact_name, iteration, ".txt")

def check_reg_values(reg_key, reg_val, artifact_name, iteration):#Send REG KEY:VALUE pair to WMI Session to extract value if exists
    print("Examining Registry Value : "+reg_key+":"+reg_val)
    if "*" in reg_key:
        print("TO DO WILDCARD HANDLING")
    else:
        command = "reg query \""+reg_key+"\" /v "+reg_val
        command = command.replace("HKEY_LOCAL_MACHINE", "HKLM").replace("HKEY_USERS", "HKU")
        rem_con.execute(command, artifact_name, iteration, ".txt")

def gather_file(file_name, artifact_name, iteration):#Send filename+extension to WMI Session for copying to remote artifact folder if exists
    if "*" in file_name:
        print("TO DO WILDCARD HANDLING")
    else:
        print("Copying File : "+file_name)
        name, extension = os.path.splitext(file_name)
        command = "copy "+file_name+" "+system_root+":\\Users\\"+elevated_username+"\Paychex_Temp_SIU"
        rem_con.execute(command, artifact_name, iteration, extension)

        #Add handler functions for other types
main()
