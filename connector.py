import subprocess, traceback, sys, wmi, subprocess, win32api, winreg, os, config, fs_interaction

class connector(): #Create, Execute, Destroy.

    def __init__(self, target, credential, password, user, domain):
        print("Connector Initiated..\n")
        self.execution_label = target+"["+user+"]"
        self.target = target
        self.credential = credential
        self.password = password
        self.user = user
        self.domain = domain
        self.root = " "
        self.envroot = " "
        self.log_buddy = fs_interaction.log_writer()

    def create_session(self): #Establish WMI Connection - will play with WinRM in future..
        print("Target : "+self.target)
        print("User Target : "+self.user)
        print("Using Credential : "+self.credential)
        #session = winrm.Session(target, auth=(credential, password), transport='kerberos') #WinRM would be easier but would require setup on remote machine.
        self.session = wmi.WMI(computer=self.target, user=self.credential, password=self.password)


    def get_sid(self): #Trying a few different ways to get SID before settling on the method below as most reliable
        #for group in self.session.Win32_Group():
        #    print(group.Caption)
        #    for user in group.associators(wmi_result_class="Win32_UserAccount"):
        #        print(user.Caption)
        #        if self.domain+"\\"+self.user == user.Caption:
        #            print("Found User, Checking SID..")
        #            print(user.Caption)
        #            print(user.SID)
        #            break
        #for item in self.session.Win32_UserAccount():
        #    #print(item)
        #    print(item.Caption)
        #    sid = item.sid
        #    print(sid)
        #    if (item.Caption == self.domain+"\\"+self.user) or (item.Caption == self.target+"\\"+self.user):
        #        break
        print("Collecting Computer Profiles..")
        profiles = []
        for user in self.session.Win32_UserProfile():#Check WMI UserProfile data
            if (self.user in user.LocalPath) and ("_alt" not in user.LocalPath):#Detect primary account
                print("User Target Found..")
                target_sid = user.SID
                user_path = user.LocalPath
                self.user_path = user.LocalPath
                print("User Path : "+user.LocalPath)
                print("User SID : "+target_sid)
            profiles.append((user.LastUseTime, user.SID, user.LocalPath))
        try:
            profiles.sort(reverse=True) #Will fail on NoneType collections
            print("Listing All Detected Profiles..")
            for profile in profiles:
                print(profile)
        except:
            print("SOFT ERROR Listing All User Profiles..")
        return(target_sid, user_path)

    def get_windir(self): #Gets default Windows Directory and by extension environment root
        with open(config.cur_dir+"\\"+config.execution_label+r"-data\files\Win32_OS.txt", "w+") as f:
            for item in self.session.Win32_OperatingSystem():
                f.write(str(item))
                print(item)
                self.root = item.WindowsDirectory
                self.envroot = item.WindowsDirectory[0]
                return item.WindowsDirectory

    def write_default(self): #Prepare folder for copying/writing/exporting artifacts
        command = "mkdir "+self.envroot+":\\Users\\"+self.credential+"\TEMPARTIFACTS" #Try to use envroot
        print("Running : "+command)
        process_id, return_value = self.session.Win32_Process.Create(CommandLine="cmd.exe /c "+command)
        if return_value != 0:
            print("Failed to create "+self.envroot+":\\Users\\"+self.credential+"\TEMPARTIFACTS' Directory..")
            print("Trying to create in "+self.user_path[0]+":\\Users\\"+self.credential+"\TEMPARTIFACTS")
            command = "mkdir "+self.user_path[0]+":\\Users\\"+self.user+"\TEMPARTIFACTS" #Use slice from detected user path
            print("Running : "+command)
            process_id, return_value = self.session.Win32_Process.Create(CommandLine="cmd.exe /c "+command)
            if return_value !=0: #NEED a directory, if we can't write, quit.
                print("Halting Execution..")
                print(traceback.print_exc(sys.exc_info()))
                exit(0)

    def execute(self, command, artifact_name, iteration):#Run Command on Remote Host
        show_window = 0
        process_startup = self.session.Win32_ProcessStartup.new()
        process_startup.ShowWindow = show_window #Hide Window
        #file_name = command.replace("/","_").replace(" ", "_").replace("\\", "_").replace(":","_").replace("<","_").replace(">","_") #Initial Naming Idea
        #print(command)
        if "wmic" in command:
            #command = command.replace("wmic", "wmic /output:"+self.envroot+":\\Users\\"+self.user+"\TEMPARTIFACTS\\"+artifact_name+str(iteration)+".txt")
            #command = "cmd.exe /c "+"\""+command+"\""+" > \""+self.envroot+":\\Users\\"+self.user+"\TEMPARTIFACTS\\"+artifact_name+str(iteration)+".txt\""
            command = command.replace("wmic","")
            command = "wmic /node:\""+self.target+"\" /user:"+self.credential+" /password:"+self.password+" "+command+" > "+self.execution_label+"-data\\"+artifact_name+".txt"  
            #print("\n"+command)
            command_censored = command.replace(self.password, "****").replace("wmic", "echo wmic")
            result_filt = subprocess.getoutput(command_censored)
            result = subprocess.getoutput(command)
            #with open(self.execution_label+"-data\\"+artifact_name+".txt", 'a+') as f:
            #    f.write(str(result))

            command = command.replace(self.password, "XXXXXXXX")
            #print("Process Executed: "+command)
            print(result)
            #process_id, return_value = self.session.Win32_Process.Create(CommandLine=command, ProcessStartupInformation=process_startup)
            #print("Process ID: "+str(process_id)+" , Return Value (0 = Success): "+str(return_value)+"\n")
        else:
            process_id, return_value = self.session.Win32_Process.Create(CommandLine=("cmd.exe /c echo "+command+" >> "+self.envroot+":\\Users\\"+self.credential+"\TEMPARTIFACTS\\"+artifact_name+str(iteration)+".txt"), ProcessStartupInformation=process_startup)
            process_id, return_value = self.session.Win32_Process.Create(CommandLine=("cmd.exe /c "+command+" >> "+self.envroot+":\\Users\\"+self.credential+"\TEMPARTIFACTS\\"+artifact_name+str(iteration)+".txt"), ProcessStartupInformation=process_startup)
            #print("Process Executed: cmd.exe /c "+command+" > "+self.envroot+":\\Users\\"+self.credential+"\TEMPARTIFACTS\\"+artifact_name+str(iteration)+".txt")
            #print("Process ID: "+str(process_id)+" , Return Value (0 = Success): "+str(return_value)+"\n")

    def connect_drive(self):
        x = 0
        try:
            command = "net view"
            cmd_result = subprocess.getoutput(command)
            if self.target.lower() in cmd_result.lower():
                print("DRIVE ALREADY MAPPED")
                x = 1
            return cmd_result
        except:
            print("ERROR running net view, need admin priveliges?")
            print(traceback.print_exc(sys.exc_info()))
            tb = traceback.format_exc()
            log_buddy.write_log("Error",str(tb))
        if x != 1:
            try:
                print("Trying to Map Target Drive..")
                if self.domain == "":
                    print("EXECUTING : net use \\\\"+self.target+"\\"+config.system_root+" /u:"+self.credential)
                    command = "net use \\\\"+self.target+"\\"+config.system_root+" /u:"+self.credential
                    self.log_buddy.write_log('Execution', command)
                    cmd_result = subprocess.getoutput(command, shell=True)
                else:
                    print("EXECUTING : net use \\\\"+self.target+"\\"+config.system_root+" /u:"+self.domain+"\\"+self.credential)
                    self.log_buddy.write_log('Execution', 'EXECUTED net use \\\\'+self.target+"\\"+config.system_root+" /u:"+self.domain+"\\"+self.credential)
                    cmd_result = subprocess.getoutput("net use \\\\\""+self.target+"\\"+config.system_root+"\" /u:"+self.domain+"\\"+self.credential, shell=True)
                print("Mapped Target Drive..")
                return cmd_result
            except:
                print("ERROR Failed to Open Connection, Last Ran Command Logged to Error Log..")
                print(traceback.print_exc(sys.exc_info()))
                exit(0)


    def disconnect_drive(self):
        try:
            print("Trying to Remove Mapped Target Drive")
            cmd_result = subprocess.getoutput(r'net use \\\\'+self.target+"\\"+config.system_root+" /delete", shell=True)
            print("UnMapped Target Drive..")
        except:
            print("Failed to Close Connection")
            print(traceback.print_exc(sys.exc_info()))
            exit(0)