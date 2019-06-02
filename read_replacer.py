import config, fs_interaction
global log_buddy


class replacer():

    def __init__(self):
        print("Data-Read Replacer Instantiated..")
        self.log_buddy = fs_interaction.log_writer()

    def replace_values(self, item):#Replace placeholder strings in artifacts with gathered data -> check for other necessary replacements
        if "%%users.userprofile%%" in item:
            item = item.replace("%%users.userprofile%%", config.base_user_dir)
        if "%%users.sid%%" in item:
            item = item.replace("%%users.sid%%", config.user_sid)
        if "%%users.username%%" in item:
            item = item.replace("%%users.username%%", config.user_target)
        if "%%users.temp%%" in item:
            item = item.replace("%%users.temp%%", config.user_local_appdata_dir+"\Temp")
        if "%%users.localappdata%%" in item:
            item = item.replace("%%users.localappdata%%", config.user_local_appdata_dir)
        if "%%users.appdata%%" in item:
            item = item.replace("%%users.appdata%%", config.user_appdata_dir)
        if "%%environ_systemroot%%" in item:
            item = item.replace("%%environ_systemroot%%", config.system_root+":\Windows")
        if "%%environ_systemdrive%%" in item:
            item = item.replace("%%environ_systemdrive%%", config.system_root+":\\")
        if ("%%environ_windir%%" in item) and (config.win_def == 0):
            item = item.replace("%%environ_windir%%", config.win_dir)
        elif ("%%environ_windir%%" in item) and (config.win_def == 1):
            item = item.replace("%%environ_windir%%", config.system_root+":\Windows")
        if "%%environ_allusersappdata%%" in item:
            item = item.replace("%%environ_allusersappdata%%", config.system_root+":\ProgramData")
        if "%%environ_programfiles%%" in item:
            item = item.replace("%%environ_programfiles%%", config.system_root+":\Program Files")
        if "%%environ_programfilesx86%%" in item:
            item = item.replace("%%environ_programfilesx86%%", config.system_root+":\Program Files (x86)")
        if "%%users.homedir%%" in item:
            item = item.replace("%%users.homedir%%", config.user_path+"\\")
        if r"\\\\" in item:
            item = item.replace(r"\\\\", r"\\")
        return item

    def wmi_replacer(self, query):
        if "ComputerSystem" in query:
            query = query.replace("ComputerSystemProduct", "ComputerSystem")
            self.log_buddy.write_log("Execution","REPLACED 'ComputerSystemProduct' WITH 'ComputerSystem' IN "+query)
        if "SystemDriver" in query:
            query = query.replace("SystemDriver", "SysDriver")
            query = query.replace("SELECT DisplayName, Description, InstallDate, Name, PathName, Status, State, ServiceType from","")
            query = query.replace("get *", "get DisplayName, Description, InstallDate, Name, PathName, Status, State, ServiceType")
            self.log_buddy.write_log("Execution","REPLACED 'SystemDriver' WITH 'SysDriver' IN "+query)
            self.log_buddy.write_log("Execution","REPLACED 'SELECT DisplayName, Description, InstallDate, Name, PathName, Status, State, ServiceType from' WITH '' IN "+query)
            self.log_buddy.write_log("Execution","REPLACED 'get *' WITH get 'DisplayName, Description, InstallDate, Name, PathName, Status, State, ServiceType' IN "+query)
        if "from Product get" in query:
            query = query.replace("SELECT Name, Vendor, Description, InstallDate, InstallDate2, Version from", "")
            query = query.replace("get *","get Name, Vendor, Description, InstallDate, InstallDate2, Version")
            self.log_buddy.write_log("Execution","REPLACED 'SELECT Name, Vendor, Description, InstallDate, InstallDate2, Version from' WITH '' IN "+query)
            self.log_buddy.write_log("Execution","REPLACED 'get *' WITH 'get Name, Vendor, Description, InstallDate, InstallDate2, Version' IN "+query)
        if "LastBootUpTime" in query:
            query = query.replace("SELECT LastBootUpTime FROM","")
            query = query.replace("get *","get LastBootUpTime")
            self.log_buddy.write_log("Execution","REPLACED 'SELECT LastBootUpTime FROM' WITH '' IN "+query)
            self.log_buddy.write_log("Execution","REPLACED 'get *' WITH 'get LastBootUpTime' IN "+query)
        if "QuickFixEngineering" in query:
            query = query.replace("QuickFixEngineering", "QFE")
            self.log_buddy.write_log("Execution","REPLACED 'QuickFixEngineering' WITH 'QFE' IN "+query)
        if "OperatingSystem" in query:
            query = query.replace("OperatingSystem","OS")
            self.log_buddy.write_log("Execution","REPLACED 'OperatingSystem' WITH 'OS' IN "+query)
        if "LogonSession" in query:
            query = query.replace("LogonSession","Logon")
            self.log_buddy.write_log("Execution","REPLACED 'LogonSession' WITH 'Logon' IN "+query)
        if "GroupUser" in query:
            query = query.replace("GroupUser where Name = \"login_users\"", "Group")
            self.log_buddy.write_log("Execution","REPLACED 'GroupUser where Name = \"login_users\"' WITH 'Group' IN "+query)
        if "PhysicalMemory" in query:
            query = query.replace("PhysicalMemory","MEMPHYSICAL")
            self.log_buddy.write_log("Execution","REPLACED 'PhysicalMemory' WITH 'MEMPHYSICAL' IN "+query)
        if "UserProfile" in query:
            query = query.replace("UserProfile WHERE SID='%%users.sid%%'", "UserAccount")
            self.log_buddy.write_log("Execution","REPLACED 'UserProfile WHERE SID='%%users.sid%%' WITH 'UserAccount' IN "+query)
        if "StartupCommand" in query:
            query = query.replace("StartupCommand", "Startup")
            self.log_buddy.write_log("Execution","REPLACED 'StartupCommand' WITH 'Startup' IN "+query)
        query = query.replace(",",".") #Because CSV
        self.log_buddy.write_log("Execution","REPLACED ',' WITH '.' IN "+query)
        return query
