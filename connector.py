import subprocess, traceback, sys, wmi, subprocess, win32api, winreg

class connector(): #Create, Execute, Destroy.

    def __init__(self, target, credential, password, user, domain):
        print("Connector Initiated..\n")
        self.target = target
        self.credential = credential
        self.password = password
        self.user = user
        self.domain = domain
        self.root = " "
        self.envroot = " "

    def create_session(self): #Establish WMI Connection - will play with WinRM in future..
        print("Target : "+self.target)
        print("User Target : "+self.user)
        print("Using Credential : "+self.credential)
        #session = winrm.Session(target, auth=(credential, password), transport='kerberos') #WinRM would be easier but would require setup/touching machine in ways I don't want to.
        self.session = wmi.WMI(self.target, user=self.credential, password=self.password)


    def get_sid(self): #Trying a few different ways to get SID
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
                print(user.LocalPath)
                print(target_sid)
            profiles.append((user.LastUseTime, user.SID, user.LocalPath))
        try:
            profiles.sort(reverse=True) #Will fail on NoneType collections
            print("Listing All Detected Profiles..")
            for p in profiles:
                print(p)
        except:
            print("ERROR listing all profiles..no big deal..")
        return(target_sid, user_path)

    def get_windir(self): #Gets default Windows Directory and by extension environment root
        for item in self.session.Win32_OperatingSystem():
            print(item)
            self.root = item.WindowsDirectory
            self.envroot = item.WindowsDirectory[0]
            print(self.root, self.envroot)
            return item.WindowsDirectory

    def write_default(self): #Prepare folder for copying/writing/exporting artifacts
        command = "mkdir "+self.envroot+":\\Users\\"+self.user+"\Paychex_Temp_SIU" #Try to use envroot
        print("Running : "+command)
        process_id, return_value = self.session.Win32_Process.Create(CommandLine="cmd.exe /c "+command)
        if return_value != 0:
            print("Failed to create "+self.envroot+":\\Users\\"+self.user+"\Paychex_Temp_SIU' Directory..")
            print("Trying to create in "+self.user_path[0]+":\\Users\\"+self.user+"\Paychex_Temp_SIU")
            command = "mkdir "+self.user_path[0]+":\\Users\\"+self.user+"\Paychex_Temp_SIU" #Use slice from detected user path
            print("Running : "+command)
            process_id, return_value = self.session.Win32_Process.Create(CommandLine="cmd.exe /c "+command)
            if return_value !=0: #NEED a directory, if we can't write, quit.
                print("Halting Execution..")
                print(traceback.print_exc(sys.exc_info()))
                exit(0)

    def execute(self, command, artifact_name, iteration, extension):#Run Command on Remote Host
        show_window = 0
        process_startup = self.session.Win32_ProcessStartup.new()
        process_startup.ShowWindow = show_window #Hide Window
        #file_name = command.replace("/","_").replace(" ", "_").replace("\\", "_").replace(":","_").replace("<","_").replace(">","_") #Initial Naming Idea
        process_id, return_value = self.session.Win32_Process.Create(CommandLine=r"cmd.exe /c "+command+" >> "+self.envroot+":\\Users\\"+self.user+"\Paychex_Temp_SIU\\"+artifact_name+str(iteration)+extension, ProcessStartupInformation=process_startup)
        #test = subprocess.check_output(["ipconfig", "/all"])
        print("Command Executed: cmd.exe /c "+command+" >> "+self.envroot+":\\Users\\"+self.user+"\Paychex_Temp_SIU\\"+artifact_name+str(iteration)+extension)
        print("Process ID: "+str(process_id)+" , Return Value (0 = Success): "+str(return_value))

    def disconnect(self):
        try:
            subprocess.call(r'net use Z: /delete', shell=True)
            print("Connection Closed Successfully")
        except:
            print("Failed to Close Connection")
            print(traceback.print_exc(sys.exc_info()))
            exit(0)