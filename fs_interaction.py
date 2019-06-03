import yaml, os, datetime, tqdm, ctypes, sys, time, colorama, traceback, config

class log_writer(): #Responsible for writing data to error/execution logs

    def __init__(self):
        #print("Log Writer Instantiated..")
        self.execution_log = config.execution_log
        self.error_log = config.error_log

    def write_log(self, type, data):
        if "\n" not in data[-2:]:
            data = data + "\n"
        if type == "Error":
            with open(self.error_log, 'a+') as f:
                f.write(str(datetime.datetime.now())+" "+data)
        elif type == "Execution":
            with open(self.execution_log, 'a+') as f:
                f.write(str(datetime.datetime.now())+" "+data)



def read_yaml_data(data, artifact_file):#Responsible for parsing YAML data structures within folder and some basic replacement with things I found worked
    import read_replacer
    replacer = read_replacer.replacer()
    yaml_data_folder = data #Name of folder storing .yaml artifact signatures
    print("Reading YAML Files...")
    yaml_files = [f for f in os.listdir(yaml_data_folder) if os.path.isfile(os.path.join(yaml_data_folder, f))]
    longest = 0
    for name in yaml_files: #Calculating longest file name to make progress bar pretty
        length = len(name)
        #print(length, longest)
        if length > longest:
            longest = len(name)
    log_buddy = log_writer()
    with open(artifact_file, 'w', newline='') as a:
        progress_bar = tqdm.tqdm(total=len(yaml_files))
        for file in yaml_files:
            progress_bar.update(1)
            difference = longest - len(file) #Finding difference between longest and current file name
            desc = file
            for x in range(0, difference): #Adding spaces corresponding to length difference
                desc = " "+desc
            progress_bar.set_description("READING FILE: "+desc)
            #print("Reading : "+file)
            #time.sleep(.1)
            try:
                with open(yaml_data_folder+"\\"+file) as f:
                    for item in yaml.load_all(f, Loader=yaml.FullLoader):
                        source_data = item.get("sources")
                        for data_feed in source_data:
                            #print("")
                            log_buddy.write_log("Execution","READING: "+item.get("name")+" in "+file+"..\n")
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
                                    query = replacer.wmi_replacer(query)
                                    query = query.replace(",",".") #Because CSV
                                    log_buddy.write_log("Execution","REPLACED ',' WITH '.' IN "+query)
                                    #print(name_space)
                                    #print(query)
                                    wmi_query_string = "wmic /namespace"+name_space+query+";"
                                    log_buddy.write_log("Execution","BUILT QUERY STRING "+wmi_query_string)
                                    #print(wmi_query_string)
                                    row = art_type+","+name+","+"\""+wmi_query_string+"\""+","+documentation.replace(",","-").replace("\n","").replace("\r","").replace("\"","'")+","+file+"\n"
                                    log_buddy.write_log("Execution", "WROTE TO ARTIFACTS.CSV : "+row)
                                    a.write(row)
                            else:
                                pass
            except:
                print(traceback.print_exc(sys.exc_info()))
                print("\nERROR Reading : "+file)
                log_buddy.write_log("Error"," "+"ERROR Reading : "+file+"..\n")
        progress_bar.close()

def setup_log_file(execution_label, error_log, execution_log):#Creates error/execution log files along with log/data directories
    global execution_log_tmp, error_log_tmp
    execution_log_tmp = execution_log
    error_log_tmp = error_log
    try:
        print("Making "+execution_label+"-logs Directory..")
        os.mkdir(execution_label+"-logs")
    except:
        print("ERROR "+execution_label+"-logs directory already exists or lacking permissions..")
    try:
        print("Making "+execution_label+"-data Directory..")
        os.mkdir(execution_label+"-data")
    except:
        print("ERROR "+execution_label+"-data directory already exists or lacking permissions..")
    try:
        print("Making "+execution_label+r"-data\files Directory..")
        cur_dir = os.getcwd()
        os.chdir(execution_label+"-data")
        os.mkdir("files")
        os.chdir(cur_dir)
    except:
        os.chdir(cur_dir)
        print("ERROR "+execution_label+r"-data\files directory already exists or lacking permissions..")
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
        