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
        if config.elevated_password:
            self.provided = 1
        else:
            self.provided = 0

    def create_session(self): #Establish WMI Connection - will play with WinRM in future..
        print("Target Device : "+self.target)
        print("User Target : "+self.user)
        print("Using Credential : "+self.credential)
        #session = winrm.Session(target, auth=(credential, password), transport='kerberos') #WinRM would be easier but would require setup on remote machine.
        self.session = wmi.WMI(computer=self.target, user=self.credential, password=self.password)
        self.log_buddy.write_log("Execution", "WMI SESSION CREATED ON "+self.target+" WITH USER "+self.credential)


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
        print("Examining Computer Profiles..")
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
            print("Listing All Detected Profiles for Reference..")
            for profile in profiles:
                print(profile)
        except:
            print("SOFT ERROR Listing All User Profiles..")
            self.log_buddy.write_log("Error","SOFT ERROR Listing All User Profiles..")
            tb = traceback.format_exc()
            self.log_buddy.write_log("Error", str(tb))
        return(target_sid, user_path)

    def get_windir(self): #Gets default Windows Directory and by extension environment root
        with open(config.cur_dir+"\\"+config.execution_label+r"-data\files\Win32_OS.txt", "w+") as f:
            for item in self.session.Win32_OperatingSystem():
                f.write(str(item))
                #print(item)
                self.root = item.WindowsDirectory
                self.envroot = item.WindowsDirectory[0]
                return item.WindowsDirectory

    def make_dir(self, dir): #Prepare folder for copying/writing/exporting artifacts
        command = "mkdir "+dir #Try to use envroot
        #print("Running : "+command)
        process_id, return_value = self.session.Win32_Process.Create(CommandLine="cmd.exe /c "+command)

        if (return_value != 0) and ("TEMPARTIFACTS" in dir):
            print("Failed to create "+dir+" Directory..")
            print("Halting Execution..")
            self.log_buddy.write_log("Error","CRITICAL ERROR CREATING DIRECTORY: "+dir)
            tb = traceback.format_exc()
            self.log_buddy.write_log("Error", str(tb))
            exit(0)
        elif return_value !=0:
            print("Failed to create " + dir + " Directory..")
            self.log_buddy.write_log("Error", "SOFT ERROR CREATING DIRECTORY: " + dir)
            tb = traceback.format_exc()
            self.log_buddy.write_log("Error", str(tb))
            return 1
        elif return_value == 0:
            #print("Created Directory :"+dir)
            self.log_buddy.write_log("Execution", "CREATED DIRECTORY: " + dir)
            return 0

    #Passwords - Either you don't provide it initially via -p XXX then provide it to connect via WMI then either DONT pass to each WMIC and individually enter or DO pass to each WMI
    #Alternative is provide initially via -p XXX then DO or DONT provide to each WMIC -> although likely in this case you wouldn't care and would provide it regardless
    def execute(self, command, artifact_name, iteration):#Run Command on Remote Host
        show_window = 0
        process_startup = self.session.Win32_ProcessStartup.new()
        process_startup.ShowWindow = show_window #Hide Window
        if "wmic" in command:
            command = command.replace("wmic","")
            if self.provided == 0:
                command = "wmic /node:\""+self.target+"\" /user:"+self.credential+" "+command+" > "+self.execution_label+"-data\WMI\\"+artifact_name+".txt"
                command_censored = command.replace(self.password, "****").replace("wmic", "echo wmic")
                result_filt = subprocess.getoutput(command_censored)
                result = subprocess.getoutput(command)
                print("Enter Password for "+self.credential+":")
            elif self.provided == 1:
                #command = "wmic /node:\""+self.target+"\" /user:"+self.credential+" /password:"+self.password+" "+command+" > "+self.execution_label+"-data\\"+artifact_name+".txt" #STDOUT to File
                command = "wmic /output:\""+self.execution_label+"-data\WMI\\"+artifact_name+".txt\" /node:\""+self.target+"\" /user:"+self.credential+" /password:"+self.password+" "+command #/output flag in WMIC testing
                command_censored = command.replace(self.password, "****").replace("wmic", "echo wmic")
                result_filt = subprocess.getoutput(command_censored)
                result = subprocess.getoutput(command)#With PW

        else:#Everything except WMIC commands
            dir = self.envroot + ":\\Users\\" + self.credential + "\TEMPARTIFACTS\\" + artifact_name
            val = self.make_dir(dir)
            if val == 0:
                dir = dir + "\\" + artifact_name + ".txt"
            else:
                dir = self.envroot + ":\\Users\\" + self.credential + "\TEMPARTIFACTS\\"+artifact_name+".txt"
            #process_id, return_value = self.session.Win32_Process.Create(CommandLine=("cmd.exe /c echo "+command+" >> "+self.envroot+":\\Users\\"+self.credential+"\TEMPARTIFACTS\\"+artifact_name+".txt"), ProcessStartupInformation=process_startup)
            #process_id, return_value = self.session.Win32_Process.Create(CommandLine=("cmd.exe /c "+command+" >> "+self.envroot+":\\Users\\"+self.credential+"\TEMPARTIFACTS\\"+artifact_name+".txt"), ProcessStartupInformation=process_startup)

            process_id, return_value = self.session.Win32_Process.Create(CommandLine=("cmd.exe /c echo "+command+" >> "+dir), ProcessStartupInformation=process_startup)
            process_id, return_value = self.session.Win32_Process.Create(CommandLine=("cmd.exe /c "+command+" >> "+dir), ProcessStartupInformation=process_startup)
            #print("Process Executed: cmd.exe /c "+command+" > "+self.envroot+":\\Users\\"+self.credential+"\TEMPARTIFACTS\\"+artifact_name+str(iteration)+".txt")
            #print("Process ID: "+str(process_id)+" , Return Value (0 = Success): "+str(return_value)+"\n")

    def connect_drive(self):
        x = 0
        y = 0
        try:
            command = "net view"
            cmd_result = subprocess.getoutput(command)
            if self.target.lower() in cmd_result.lower():
                print("DRIVE ALREADY MAPPED")
                self.log_buddy.write_log('Execution', "DRIVE DETECTED IN RESULT OF 'NET VIEW' COMMAND")
                x = 1
            return cmd_result
        except:
            y = 1
            print("SOFT ERROR running net view, need admin priveliges?")
            self.log_buddy.write_log('Error', "SOFT ERROR RUNNING 'NET VIEW'")
            print(traceback.print_exc(sys.exc_info()))
            tb = traceback.format_exc()
            log_buddy.write_log("Error",str(tb))
        if (x == 0) or (y==1):
            try:
                print("Trying to Map Target Drive..")
                if self.domain == "":
                    print("EXECUTING : net use \\\\"+self.target+"\\"+config.system_root+" /u:"+self.credential)
                    command = "net use \\\\"+self.target+"\\"+config.system_root+" /u:"+self.credential
                    self.log_buddy.write_log('Execution', command)
                    cmd_result = subprocess.getoutput(command)
                else:
                    print("EXECUTING : net use \\\\"+self.target+"\\"+config.system_root+"$ /u:"+self.domain+"\\"+self.credential)
                    self.log_buddy.write_log('Execution', 'EXECUTED net use \\\\'+self.target+"\\"+config.system_root+"$ /u:"+self.domain+"\\"+self.credential) #why $ vs no $
                    command = ['net', 'use', "\\\\"+self.target+"\\"+config.system_root+"$", "/u:"+self.domain+"\\"+self.credential]
                    #cmd_result = subprocess.run("net use \\\\\""+self.target+"\\"+config.system_root+"$\" /u:"+self.domain+"\\"+self.credential, shell=True
                    cmd_result = subprocess.run(command, shell=True)
                self.log_buddy.write_log('Execution', "TARGET DRIVE SUCCESSFULLY MAPPED")
                print("Mapped Target Drive..")
                return cmd_result
            except:
                print("CRITICAL ERROR Failed to Map Drive, Last Ran Command Logged to Execution Log..")
                tb = traceback.format_exc()
                self.log_buddy.write_log("Error", str(tb))
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