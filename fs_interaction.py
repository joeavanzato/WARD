import yaml, os, datetime, tqdm, ctypes, sys, time, colorama

def read_yaml_data(data, artifact_file):
    yaml_data_folder = data #Name of folder storing .yaml artifact signatures
    print("Reading YAML Files...")
    yaml_files = [f for f in os.listdir(yaml_data_folder) if os.path.isfile(os.path.join(yaml_data_folder, f))]
    with open(artifact_file, 'w', newline='') as a:
        progress_bar = tqdm.tqdm(total=len(yaml_files))
        for file in yaml_files:
            progress_bar.update(1)
            progress_bar.set_description("Reading: "+file)
            #print("Reading : "+file)
            time.sleep(.1)
            try:
                with open(yaml_data_folder+"\\"+file) as f:
                    for item in yaml.load_all(f, Loader=yaml.FullLoader):
                        source_data = item.get("sources")
                        for data_feed in source_data:
                            #print("")
                            if "Windows" in str(item.get("supported_os")):
                                #print(item.get("name"))
                                name = item.get("name")
                                #print(item.get("doc"))
                                documentation = item.get("doc")
                                #print(data_feed.get("type"))
                                #print(item.get("sources"))
                                #print(item.get("supported_os"))
                                #print(data_feed)
                                art_type = data_feed.get("type")
                                if (art_type == "FILE") or (art_type == "DIRECTORY"):
                                    attributes = data_feed.get("attributes")
                                    paths = attributes.get("paths")
                                    path_string = ""
                                    len(paths)
                                    x = 0
                                    for value in paths:
                                        if x == 0: 
                                            path_string = value
                                        else:
                                            path_string = path_string + ";" + value
                                        x = x + 1
                                    row = art_type+","+name+","+path_string+","+documentation.replace(",","-").replace("\n","").replace("\r","").replace("\"","'")+","+file+"\n"
                                    a.write(row)
                                if art_type == "REGISTRY_KEY":
                                    attributes = data_feed.get("attributes")
                                    keys = attributes.get("keys")
                                    key_string = ""
                                    x = 0
                                    for value in keys:
                                        if x == 0:
                                            key_string = value
                                        else:
                                            key_string = key_string + ";" + value
                                        x = x + 1
                                    row = art_type+","+name+","+key_string+","+documentation.replace(",","-").replace("\n","").replace("\r","").replace("\"","'")+","+file+"\n"
                                    a.write(row)
                                if art_type == "REGISTRY_VALUE":
                                    attributes = data_feed.get("attributes")
                                    key_pairs = attributes.get("key_value_pairs")
                                    key_value_string = ""
                                    for item in key_pairs:
                                        reg_value = item.get("value")
                                        reg_key = item.get("key")
                                        key_value_string = reg_key +";"+reg_value
                                    row = art_type+","+name+","+key_value_string+","+documentation.replace(",","-").replace("\n","").replace("\r","").replace("\"","'")+","+file+"\n"
                                    a.write(row)
                                if art_type == "COMMAND":
                                    attributes = data_feed.get("attributes")
                                    cmd_arg_string = ""
                                    cmd = attributes.get("cmd")
                                    args = ""
                                    x = 0
                                    for item in attributes.get("args"):
                                        if x == 0:
                                            args = item
                                            x = x + 1
                                        else:
                                            args = args + " " + item
                                    cmd_arg_string = cmd+";"+args
                                    #print(cmd_arg_string)
                                    row = art_type+","+name+","+cmd_arg_string+","+documentation.replace(",","-").replace("\n","").replace("\r","").replace("\"","'")+","+file+"\n"
                                    a.write(row)
                                if art_type == "PATH": #Don't really need these right now I guess, revisit in future..
                                    attributes = data_feed.get("attributes")
                                    #print(attributes)
                                if art_type == "WMI":
                                    attributes = data_feed.get("attributes")
                                    #print(attributes)
                                    if 'base_object' in attributes:
                                        name_space = attributes.get("base_object")
                                        name_space = name_space.replace(r"\\\\",r"\\")
                                        name_space = name_space.replace(r"winmgmts:\root",r":\\root")
                                        name_space = name_space + " " + "path"
                                    else:
                                        name_space = r":\\root\cimv2"
                                    query = attributes.get("query")
                                    query = query.replace("Win32_","")
                                    query = query.replace(r"SELECT * FROM","").replace(r"SELECT * from","")
                                    query = query+" get * /value"
                                    if "ComputerSystem" in query:
                                        query = query.replace("ComputerSystemProduct", "ComputerSystem")
                                    if "SystemDriver" in query:
                                        query = query.replace("SystemDriver", "SysDriver")
                                        query = query.replace("SELECT DisplayName, Description, InstallDate, Name, PathName, Status, State, ServiceType from","")
                                        query = query.replace("get *", "get DisplayName, Description, InstallDate, Name, PathName, Status, State, ServiceType")
                                    if "from Product get" in query:
                                        query = query.replace("SELECT Name, Vendor, Description, InstallDate, InstallDate2, Version from", "")
                                        query = query.replace("get *","get Name, Vendor, Description, InstallDate, InstallDate2, Version")
                                    if "LastBootUpTime" in query:
                                        query = query.replace("SELECT LastBootUpTime FROM","")
                                        query = query.replace("get *","get LastBootUpTime")
                                    if "QuickFixEngineering" in query:
                                        query = query.replace("QuickFixEngineering", "QFE")
                                    if "OperatingSystem" in query:
                                        query = query.replace("OperatingSystem","OS")
                                    if "LogonSession" in query:
                                        query = query.replace("LogonSession","Logon")
                                    if "GroupUser" in query:
                                        query = query.replace("GroupUser where Name = \"login_users\"", "Group")
                                    if "PhysicalMemory" in query:
                                        query = query.replace("PhysicalMemory","MEMPHYSICAL")
                                    if "UserProfile" in query:
                                        query = query.replace("UserProfile WHERE SID='%%users.sid%%'", "UserAccount")
                                    if "StartupCommand" in query:
                                        query = query.replace("StartupCommand", "Startup")
                                    query = query.replace(",",".")
                                    #print(name_space)
                                    #print(query)
                                    wmi_query_string = "wmic /namespace"+name_space+query+";"
                                    #print(wmi_query_string)
                                    row = art_type+","+name+","+"\""+wmi_query_string+"\""+","+documentation.replace(",","-").replace("\n","").replace("\r","").replace("\"","'")+","+file+"\n"
                                    a.write(row)
                            else:
                                pass
                with open(execution_logx, 'a+') as f:
                    f.write(str(datetime.datetime.now())+" "+"Reading : "+file+"..\n")
            except:
                print("ERROR Reading : "+file)
                with open(error_logx, 'a+') as f:
                    f.write(str(datetime.datetime.now())+" "+"ERROR Reading : "+file+"..\n")
        progress_bar.close()

def setup_log_file(execution_label, error_log, execution_log):
    global execution_logx, error_logx
    execution_logx = execution_log
    error_logx = error_log
    try:
        print("Making "+execution_label+"-'logs' Directory..")
        os.mkdir(execution_label+"-logs")
    except:
        print("ERROR "+execution_label+"-'logs' directory already exists..")
    try:
        print("Making "+execution_label+"-'data' Directory..")
        os.mkdir(execution_label+"-data")
    except:
        print("ERROR "+execution_label+"-'data' directory already exists..")
    mode = 'a' if os.path.exists(error_log) else 'w'
    with open(error_log, mode):
        print("Error Log Created..")
    mode = 'a' if os.path.exists(execution_log) else 'w'
    with open(execution_log, mode):
        print("Execution Log Created..")
    with open(execution_log, 'w+') as f:
        f.write(str(datetime.datetime.now())+" "+execution_label+"-'log' Directory Created..\n")
        f.write(str(datetime.datetime.now())+" "+execution_label+"-'data' Directory Created..\n")
        f.write(str(datetime.datetime.now())+" "+"Error Log Created..\n")
        f.write(str(datetime.datetime.now())+" "+"Execution Log Created..\n")
        