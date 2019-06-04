import csv, time, sys, argparse, win32api, win32net, traceback, connector, getpass, wmi, os, fs_interaction, config, stringops, read_replacer, datetime, tqdm, ctypes, colorama, time, subprocess
parser = argparse.ArgumentParser(usage = '\n Remote Artifact Analysis and Retrieval\n -t -- [Target Host-Name or IP Address (Only One)]\n -c -- UserName to Connect Via (Alt Account)\n -u -- Target User Name to Inspect\n -build -- Use to Unpack YAML data into Artifact.csv on first run or update \n -l -- Use to indicate operation on Local Host')
parser.add_argument("-t", "--target", help='Specify Target Host Name or IP Address', required = True) #Target machine
parser.add_argument("-c", "--credential", help='Specify UID to Connect VIA', required = True) #Credential/UserName for Access
parser.add_argument("-u", "--user_target", help='Specify UID to Target', required = True) #Target User for Analysis
parser.add_argument("-l", "--local", help='Ignores target if specified, operates on local host', required = False, action="store_true") #Target User for Analysis
parser.add_argument("-a", "--admin", help='Use if running in Domain Administrator cmdline environment', required = False, action="store_true") #If admin, can use winreg on local/direct WMI, else need to authenticate and perform on remote. Does Nothing Yet..
parser.add_argument("-b", "--build", help='Use to build artifacts.csv from YAML Data', required = False, action="store_true") 
parser.add_argument("-p", "--password", help='Use with -c to avoid password prompts and execute wmic with /password: flag in cmdline', required=False)
parser.add_argument("-d", "--domain", help="Provide domain name if working within one", required=False)
args = parser.parse_args()

#print(traceback.print_exc(sys.exc_info()))
#TO DO - Make user_target non-required and just iterate through all detected users on system - should be fairly simple.
#TO DO - Implement Operation on Local Host
#TO DO - Implement checks based on 'admin' flag that will use winreg locally to enumerate reg keys/values instead of remote execution/collection
#TO DO - Add Recursive Registry/File Copy Support, Ensure Integrity that actions reported are actually occurring, build out log writing
#Implement VSS Shadow Copy to pull 'in use' files?  Or something else?  Hmm...maybe look at Active Shadow Copy and pull out of that?

#TO DO - IF RUNNING IN DOMAIN ADMINISTRATOR TERMINAL PERMISSIONS - WMI  IS ONLY ATTEMPTED USE FOR CMD EXECUTION - REG KEY/VALUE ENUMERATION, MAPPING/COPYING FILES AND WMIC CAN ALL BE DONE LOCALLY

global type_dict, values_dict, doc_dict, base_user_dir, user_appdata_dir, user_local_appdata_dir, user_roaming_appdata_dir, log_buddy, cur_dir, elevated_password
current_datetime = datetime.datetime.now()
target = args.target
cur_dir = os.getcwd()
elevated_username = args.credential
user_target = args.user_target
admin_priv = args.admin
build = args.build
if args.password is not None:
    elevated_password = args.password
    config.elevated_password = elevated_password
if args.domain is not None:
    domain = args.domain
    config.domain = domain
else:
    domain = ""

execution_label = target+"["+user_target+"]"
artifact_file=execution_label+"-data/artifacts.csv" #Input Artifact File in format "TYPE, NAME, ; separated VALUES, DOCUMENTATION
execution_log=execution_label+"-logs/execution_log.txt"
error_log=execution_label+"-logs/error_log.txt"
yaml_data_folder = "yamldata" #Name of folder storing .yaml artifact signatures

kernel32 = ctypes.windll.kernel32
config.cur_dir = cur_dir
config.target = target
config.elevated_username = elevated_username
config.user_target = user_target
config.admin_priv = admin_priv
config.build = build
config.yaml_data_folder = yaml_data_folder
config.execution_label= execution_label
config.artifact_file = artifact_file
config.execution_log = execution_log
config.error_log = error_log

def main():#Because every tool has ASCII art, right?
    global log_buddy
    print("########################################\n")
    print(" _       _____    ____  ____ ")
    print("| |     / /   |  / __ \/ __ \\")
    print("| | /| / / /| | / /_/ / / / /")
    print("| |/ |/ / ___ |/ _, _/ /_/ / ")
    print("|__/|__/_/  |_/_/ |_/_____/  ")
    print("########################################\n")
    print("Windows Artifact Retrieval and Discovery\n")
    print("Joe Avanzato , github.com/joeavanzato\n")
    print("########################################\n")

    fs_interaction.setup_log_file(execution_label, error_log, execution_log)
    log_buddy = fs_interaction.log_writer()
    if build == True:
        fs_interaction.read_yaml_data(yaml_data_folder, artifact_file)
    parse_artifacts() #Read the Built File (TYPE, NAME, VALUES(; sep.), DOCUMENTATION
    separate_into_named_lists() #Separate the gathered data into various lists
    establish_connection() #Prepare Connection to Remote Host
    test_connection() #Verify working connection with ipconfig
    parse_and_pass() #Check artifact type and pass to helper functions for cmd execution
    fs_interaction.copy_from_host() #Copy all collected artifacts from target to localhost



def establish_connection(): #Setup WMI Connection, Get SID, UserPath and default WINDIR
    log_buddy.write_log("Execution", "ESTABLISHING REMOTE CONNECTION..")
    global rem_con, user_sid, user_path, system_root, base_user_dir, user_appdata_dir, user_local_appdata_dir, user_roaming_appdata_dir, win_dir, win_def
    print("\nBuilding Remote Connection..\n")
    try:
        if args.password is None:
            log_buddy.write_log("Execution", "PROMPTING FOR PASSWORD")
            password = getpass.getpass(prompt="Password for "+elevated_username+":")
            log_buddy.write_log("Execution", "RECEIVED PASSWORD FROM USER")
            log_buddy.write_log("Execution", "CREATING OBJECT Connector.Connector")
            rem_con = connector.connector(target, elevated_username, password, user_target, domain)
        else:
            log_buddy.write_log("Execution", "PASSWORD PROVIDED AT STARTUP")
            rem_con = connector.connector(target, elevated_username, elevated_password, user_target, domain)
    except:
        print("CRITICAL ERROR Instantiating Connector.Connector")
        log_buddy.write_log("Error","CRITICAL ERROR Instantiating Connector.Connector")
        #print(traceback.print_exc(sys.exc_info()))
        tb = traceback.format_exc()
        log_buddy.write_log("Error",str(tb))
        exit(0)
    try:
        rem_con.create_session()
    except:
        print("CRITICAL ERROR Initializing WMI Connection..does your credential have Remote Access?")
        log_buddy.write_log("Error","CRITICAL ERROR Initializing WMI Connection..does your credential have Remote Access?")
        tb = traceback.format_exc()
        log_buddy.write_log("Error",str(tb))
        exit(0)
    try:#Prepare some paths for replacement in artifacts
        user_sid, user_path = rem_con.get_sid()
        system_root = user_path[0]
        base_user_dir = system_root+":\\Users\\" + user_target
        user_appdata_dir = base_user_dir+"\\"+"AppData"
        user_local_appdata_dir = user_appdata_dir+"\\"+"Local"
        user_temp_dir = user_local_appdata_dir+"\\"+"Temp"
        user_roaming_appdata_dir = user_appdata_dir+"\\"+"Roaming"
        config.user_sid = user_sid
        config.user_path = user_path
        config.system_root = system_root
        config.base_user_dir = base_user_dir
        config.user_appdata_dir = user_appdata_dir
        config.user_local_appdata_dir = user_local_appdata_dir
        config.user_roaming_appdata_dir = user_roaming_appdata_dir
        config.user_temp_dir = user_temp_dir
        win_def = 0
        config.win_def = win_def
        log_buddy.write_log("Execution","FOUND USER SID: "+user_sid)
        log_buddy.write_log("Execution","FOUND USER PATH: "+user_path)
        log_buddy.write_log("Execution","CALCULATED USER DIR: "+user_sid)
        log_buddy.write_log("Execution","CALCULATED USER APPDATA DIR: "+user_appdata_dir)
        log_buddy.write_log("Execution","CALCULATED USER APPDATA DIR: "+user_appdata_dir)
    except:#NEED SID for real functionality
        print("CRITICAL ERROR Getting Target User SID..")
        log_buddy.write_log("Error","CRITICAL ERROR Getting Target User SID..")
        #print(traceback.print_exc(sys.exc_info()))
        tb = traceback.format_exc()
        log_buddy.write_log("Error",str(tb))
        exit(0)
    try:
        log_buddy.write_log("Execution","CHECKING FOR WINDIR DEFAULT LOCATION")
        win_dir = rem_con.get_windir()
        config.win_dir = win_dir
        print("Found WINDIR : "+win_dir)
        log_buddy.write_log("Execution","FOUND DEFAULT WINDIR: "+win_dir)
    except:
        win_def = 1
        config.win_def = win_def
        print("Failed Finding default WINDIR, using "+system_root+":\Windows")
        print("SOFT ERROR Finding default WINDIR, using "+system_root+":\Windows")
        log_buddy.write_log("Error","SOFT ERROR Finding default WINDIR, using "+system_root+":\Windows")
        tb = traceback.format_exc()
        log_buddy.write_log("Error",str(tb))
    try:
        print("Creating TEMPARTIFACT Directory on "+target)
        dir = system_root+":\\Users\\"+elevated_username+"\TEMPARTIFACTS"
        rv = rem_con.make_dir(dir)
        if rv == 0:
            log_buddy.write_log("Execution", "Successfully Created Remote TEMPARTIFACT DIR")
        else:
            print("ERROR CREATING TEMPARTIFACTS DIR")
    except:
        print("CRITICAL ERROR Creating TEMPARTIFACT DIR")
        log_buddy.write_log("Error","CRITICAL ERROR Creating TEMPARTIFACT DIR")
        tb = traceback.format_exc()
        log_buddy.write_log("Error",str(tb))
        exit(0)
    try:
        print("Mapping Network Drive..")
        result = rem_con.connect_drive()
        #print(result)
        log_buddy.write_log("Execution", target+" SUCCESSFULLY MAPPED")
        #if ("The command completed successfully." in str(result)): #RE DO THIS SECTION
        #    pass
        #else:
        #    print("CRITICAL ERROR Mapping Network Drive")
        #    log_buddy.write_log("Error","CRITICAL ERROR Mapping Network Drive")
        #    tb = traceback.format_exc()
        #    log_buddy.write_log("Error",str(tb))
        #    exit(0)
    except:
        print("CRITICAL ERROR Mapping Network Drive")
        log_buddy.write_log("Error","CRITICAL ERROR Mapping Network Drive")
        tb = traceback.format_exc()
        log_buddy.write_log("Error",str(tb))
        exit(0)

def test_connection():#Run basic command, make sure nothing breaks, could probably use return_value != 0 also
    print("\nVerifying Connectivity with 'ipconfig /all'..")
    command = 'ipconfig /all'
    try:
        log_buddy.write_log("Execution","EXECUTING 'ipconfig /all' ON "+target)
        rem_con.execute(command, "ipconfig", 0)
        print("Completed Successfully, Connection Verified..")
    except:
        print("CRITICAL ERROR Executing Command..Does the User Account lack WMI permissions?")
        log_buddy.write_log("Error","CRITICAL ERROR Executing Command..Does the User Account lack Remote WMI permissions?  Password Typo?")
        print(traceback.print_exc(sys.exc_info()))
        tb = traceback.format_exc()
        log_buddy.write_log("Error",str(tb))
        exit(0)

def parse_and_pass():#Separate values in individual artifact types and send to handler function, TO DO REGK
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    sys.stdout.write(u"\u001b[1000D")
    sys.stdout.flush()
    so = stringops.string_operator()
    replacer=read_replacer.replacer()

    print("\nChecking Directory Contents...")
    log_buddy.write_log("Execution","CHECKING DIRECTORIES")
    progress_bar = tqdm.tqdm(total=count_directories)
    y = so.get_longest(directories)
    log_buddy.write_log("Execution","PROGRESS BAR CREATED")
    for item in directories:
        log_buddy.write_log("Execution","CHECKING ARTIFACT NAME: "+item)
        desc = so.mod_difference(item,y)
        progress_bar.set_description(desc)
        #print(item)
        artifact_name = item
        value_raw = values_dict.get(item)
        #print(value_raw)
        item_list = replacer.replace_values(value_raw)
        items_list = item_list.split(";")
        x = 0
        for item in items_list:
            log_buddy.write_log("Execution","CHECKING ARTIFACT VALUE: "+item)
            check_dir_contents(item, artifact_name, x)
            x = x + 1
        progress_bar.update(1)
    progress_bar.close()

    print("\nChecking Registry Values...")
    log_buddy.write_log("Execution","CHECKING REGISTRY KEY:VALUE PAIRS")
    y = so.get_longest(registry_values)
    progress_bar2 = tqdm.tqdm(total=count_reg_values)
    log_buddy.write_log("Execution","PROGRESS BAR CREATED")
    for item in registry_values:
        log_buddy.write_log("Execution","CHECKING ARTIFACT NAME: "+item)
        desc = so.mod_difference(item,y)
        progress_bar2.set_description(desc)
        artifact_name = item
        value_raw = values_dict.get(item)
        temp_values_dict = so.split_items(value_raw)
        if temp_values_dict == 1:
            print("ERROR SPLITTING")
            progress_bar2.update(1)
            pass
        #print("\nArtifact Name: " + artifact_name)
        x = 0 
        for key, value in temp_values_dict.items():
            log_buddy.write_log("Execution","CHECKING ARTIFACT VALUE: "+key+":"+value)
            try:
                key = replacer.replace_values(key)
                reg_key = key
                reg_value = value
                #time.sleep(.2)
                check_reg_values(reg_key, reg_value, artifact_name, x)
                x = x + 1
            except:
                print("Error Reading Key:Value "+reg_key+":"+reg_value)
                x = x + 1
        progress_bar2.update(1)
    progress_bar2.close()

    print("\nCopying File Artifacts...")
    log_buddy.write_log("Execution","COPYING FILES")
    progress_bar3 = tqdm.tqdm(total=count_files)
    y = so.get_longest(files)
    log_buddy.write_log("Execution","PROGRESS BAR CREATED")
    for item in files:
        log_buddy.write_log("Execution","CHECKING ARTIFACT NAME: "+item)
        desc = so.mod_difference(item,y)
        progress_bar3.set_description(desc)
        artifact_name = item
        progress_bar.set_description(item)
        value_raw = values_dict.get(item)
        item_list = replacer.replace_values(value_raw)
        file_list = item_list.split(";")
        #print("\nArtifact Name: " + artifact_name)
        x = 0
        for file in file_list:
            log_buddy.write_log("Execution","COPYING FILE: "+file)
            desc = file
            try:
                #print(value_raw)
                #print(file)
                #time.sleep(.1)
                gather_file(file, artifact_name, x)
                x = x + 1
            except:
                print(traceback.print_exc(sys.exc_info()))
                print("ERROR copying file '"+file+"' in artifact "+artifact_name+"'")
                x = x + 1

                tb = traceback.format_exc()
                log_buddy.write_log("Error",str(tb))

            progress_bar3.update(1)
    progress_bar3.close()

    print("\nExecuting Commands through WMI..")
    log_buddy.write_log("Execution","RUNNING COMMANDS REMOTELY THROUGH WMI")
    progress_bar4 = tqdm.tqdm(total=count_commands)
    y = so.get_longest(commands)
    log_buddy.write_log("Execution","PROGRESS BAR CREATED")
    for item in commands:
        log_buddy.write_log("Execution","CHECKING ARTIFACT NAME: "+item)
        desc = so.mod_difference(item,y)
        progress_bar4.set_description(desc)
        artifact_name = item
        value_raw = values_dict.get(item)
        item_list = replacer.replace_values(value_raw)
        cmd_list = item_list.split(";")
        #print("\nArtifact Name: "+ artifact_name)
        x = 0
        for cmd in cmd_list:
            if cmd == "":
                pass
            #print(cmd)
            log_buddy.write_log("Execution","EXECUTING COMMAND: "+cmd)
            if x == 0:
                progress_bar4.update(1)
                try:
                    run_command(cmd_list[x]+" "+cmd_list[x+1], artifact_name, x)
                    x = x + 2
                except:
                    print("ERROR executing "+cmd)
                    x = x + 2
            elif x%2 != 0:
                progress_bar4.update(1)
                try:
                    run_command(cmd_list[x]+" "+cmd_list[x+1], artifact_name, x)
                    x = x + 2
                except:
                    print("ERROR executing "+cmd)
                    x = x + 2
            #progress_bar4.update(1)
    progress_bar4.close()


    print("\nExecuting WMIC Commands..")
    log_buddy.write_log("Execution","RUNNING WMIC COMMANDS LOCALLY")
    progress_bar5 = tqdm.tqdm(total=count_wmic_cmds)
    y = so.get_longest(wmic_cmds)
    log_buddy.write_log("Execution","PROGRESS BAR CREATED")
    for item in wmic_cmds:
        log_buddy.write_log("Execution","CHECKING ARTIFACT NAME: "+item)
        desc = so.mod_difference(item,y)
        progress_bar5.set_description(desc)
        artifact_name = item
        value_raw = values_dict.get(item)
        item_list = replacer.replace_values(value_raw)
        wmic_list = item_list.split(";")
        #print("\nArtifact Name: "+ artifact_name)
        x = 0
        for cmd in wmic_list:
            log_buddy.write_log("Execution","RUNNING WMIC COMMAND: "+cmd)
            if "." in cmd:
                cmd = cmd.replace(".",",")
            #print(cmd)
            if cmd == "":
                x = x + 1
                pass
            else:
                progress_bar5.update(1)
                try:
                    run_command(cmd, artifact_name, x)
                except:
                    d = "d"
            x = x + 1
            #progress_bar5.update(1)
    progress_bar5.close()
            
def parse_artifacts():
    global type_dict, values_dict, doc_dict, artifact_count, category_dict
    type_dict = {}
    values_dict = {}
    doc_dict = {}
    category_dict = {}
    print("\nLoading Artifact Data from 'artifacts.csv'..")
    with open(artifact_file, 'r') as f:
        error_count = 0
        line_count = 0
        for line in f:
            try:
                atype, name, values, doc, cat = line.split(",")
                atype = atype.replace("\"", "").strip()
                name = name.replace("\"", "").strip()
                values=values.replace("\"", "").strip()
                doc=doc.replace("\"", "").strip()
                type_dict[name] = atype
                values_dict[name] = values
                doc_dict[name] = doc
                category_dict[name] = cat
                #print(atype+" "+name+" "+values+" "+doc)
                line_count = line_count + 1
            except:
                #print(traceback.print_exc(sys.exc_info()))
                print("ERROR Loading Data on Line "+str(line_count))
                error_count = error_count + 1
                pass

    artifact_count = 0
    for key in doc_dict.items():
        artifact_count = artifact_count + 1
    print("Loaded Types, Names, Values and Documentation with "+str(error_count)+" Errors..")
    print("Total of "+str(artifact_count)+" separate artifact definitions found in database..")

def separate_into_named_lists(): #Add lists for other types, etc
    print("Separating Data..\n")
    global registry_keys, registry_values, files, commands, directories, wmic_cmds, count_reg_keys, count_reg_values, count_files, count_commands, count_directories, count_wmic_cmds
    registry_keys = []
    registry_values = []
    files = []
    commands = []
    directories = []
    wmic_cmds = []

    for key, value in type_dict.items(): #Rename according to proper artifact names, add other artifact types
        if value == "REGISTRY_KEY":
            registry_keys.append(key)
        elif value == "REGISTRY_VALUE":
            registry_values.append(key)
        elif value == "FILE":
            files.append(key)
        elif value == "COMMAND":
            commands.append(key)
        elif value == "DIRECTORY":
            directories.append(key)
        elif value == "WMI":
            wmic_cmds.append(key)
    count_reg_keys = 0
    count_reg_values = 0
    count_files = 0
    count_commands = 0
    count_directories = 0
    count_wmic_cmds = 0 
    for item in registry_keys:
        item_values = values_dict.get(item)
        item_values = item_values.split(";")
        for item in item_values:
            count_reg_keys = count_reg_keys + 1
    for item in registry_values:
        item_values = values_dict.get(item)
        item_values = item_values.split(";")
        for item in item_values:
            count_reg_values = count_reg_values + 1
    count_reg_values = count_reg_values / 2
    for item in files:
        item_values = values_dict.get(item)
        item_values = item_values.split(";")
        for item in item_values:
            count_files = count_files + 1
    for item in commands:
        item_values = values_dict.get(item)
        item_values = item_values.split(";")
        for item in item_values:
            count_commands = count_commands + 1
    for item in directories:
        item_values = values_dict.get(item)
        item_values = item_values.split(";")
        for item in item_values:
            count_directories = count_directories + 1
    count_commands = count_commands / 2
    for item in wmic_cmds:
        item_values = values_dict.get(item)
        item_values = item_values.split(";")
        for item in item_values:
            count_wmic_cmds = count_wmic_cmds + 1
    count_wmic_cmds = count_wmic_cmds / 2
    print("REGISTRY KEY ENTRIES : "+str(count_reg_keys)) #Add print for other types
    print("REGISTRY KEY:VALUE ENTRIES : "+str(count_reg_values))
    print("FILE ENTRIES : "+str(count_files))
    print("COMMAND ENTRIES : "+str(count_commands/2))
    print("DIRECTORY ENTRIES : "+str(count_directories))
    print("WMI QUERIES : "+str(count_wmic_cmds/2))


def check_dir_contents(directory, artifact_name, iteration):#Send directory path to WMI Session for 'dir' execution
    #print("\nArtifact Name: "+artifact_name)
    #print("Examining Contents of Directory : " + directory)
    if "*" in directory:
        directory = directory.replace("*","")
        command = "dir /s "+directory
    else:
        command = "dir "+directory
    rem_con.execute(command, artifact_name, iteration)

def check_reg_values(reg_key, reg_val, artifact_name, iteration):#Send REG KEY:VALUE pair to WMI Session to extract value if exists
    #print("Examining Registry Value : "+reg_key+":"+reg_val)
    if "*" in reg_key:
        #print("TO DO WILDCARD HANDLING")
        pass
    else:
        command = "reg query \""+reg_key+"\" /v \""+reg_val+"\""
        command = command.replace("HKEY_LOCAL_MACHINE\\", "HKLM\\").replace("HKEY_USERS\\", "HKU\\").replace("HKEY_CURRENT_USER\\", "HKCU\\")
        rem_con.execute(command, artifact_name, iteration)


#Copying Files is interesting - difficult and not.
#Couldn't decide between xcopy / robocopy - robocopy seems nicer but requires more work to fit syntax properly compared to xcopy, which is closer to normal copy syntax
#Copying locally vs copying through commands sent in WMI to new cmd.exe process remotely - Locally obviously has to run as local user..or does it?  This is the main restriction on Map Drive -> Copy Direct Local, hard to run as admin user when cmd is not, especially cross-domain
#Copying remote - since WMI is initiated with the destination user, it is potentially easier to use this cross-domain compared to local user copy permissions


def gather_file(file_name, artifact_name, iteration):#Send filename+extension to WMI Session for copying to remote artifact folder if exists
    file_name = '\\\\' + str(target) + "\\" + file_name
    file_name = "\""+file_name+"\""
    if admin_priv == True:
        file_name = file_name.replace(":", "$")
        command = "icacls "+file_name+" /grant "+elevated_username+":F "
        rem_con.execute(command, artifact_name, iteration)

    if "*" in file_name:
        #print("\n"+file_name)
        #print("TO DO WILDCARD HANDLING")
        try:
            file, ext = os.path.splitexe(file_name)
            split = 1
        except:
            split = 0
        x = 0
        for character in file_name:
            if character == "*":
                #print(str(x))
                wc_position = x
                break
            x = x + 1
        if "*" == file_name[-1:]:
            #print("Doing Full Recursive Copy..")
            file_name = file_name.replace("**","*")
            file_name = file_name.replace(":","")
            #command = "robocopy "+file_name+" "+system_root+":\\Users\\"+elevated_username+"\TEMPARTIFACTS /C /D /Y /I /E /Z /NP /R:5 /W:5"
            command = "xcopy "+file_name+" "+system_root+":\\Users\\"+elevated_username+"\TEMPARTIFACTS /s/h/y" #Remote - Useful for running when not on domains
            rem_con.execute(command, artifact_name, iteration)


    else:
        #print("Copying File : "+file_name)
        #name, extension = os.path.splitext(file_name)
        if domain == "":
            file_name = file_name.replace(":","")
        else:
            file_name = file_name.replace(":","$")
        #command = "robocopy "+file_name+" "+system_root+":\\Users\\"+elevated_username+"\TEMPARTIFACTS /C /D /Y /I /E /Z /NP /R:5 /W:5" #Remote - Useful for running when not on domains
        command = "xcopy "+file_name+" "+system_root+":\\Users\\"+elevated_username+"\TEMPARTIFACTS /h/y" #Remote - Useful for running when not on domains/non-admin cmdprompts
        #command = "copy "+file_name+" "+cur_dir+"\\"+execution_label+r"-data\files" #Local - Better for domains, copy via domain account permissions
        #command_split = command.split(" ")
        #print("\nEXECUTING : "+command)
        #cmd_result = subprocess.run(command, shell=True)
        rem_con.execute(command, artifact_name, iteration)

def run_command(command, artifact_name, iteration):
    #print("Running Command : "+command)
    rem_con.execute(command, artifact_name, iteration)

        #Add handler functions for other types
main()