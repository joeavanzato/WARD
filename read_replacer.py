import config, fs_interaction
global log_buddy


class replacer():

    def __init__(self):
        print("Data-Read Replacer Instantiated..")
        self.log_buddy = fs_interaction.log_writer()

    def replace_values(self, item):#Replace placeholder strings in artifacts with gathered data -> check for other necessary replacements
        item_old = item
        if "%%users.userprofile%%" in item:
            item = item.replace("%%users.userprofile%%", config.base_user_dir)
            self.log_buddy.write_log("Execution","REPLACED '%%users.userprofile%%' WITH "+config.base_user_dir+" IN "+item_old)
        if "%%users.sid%%" in item:
            item = item.replace("%%users.sid%%", config.user_sid)
            self.log_buddy.write_log("Execution","REPLACED '%%users.sid%%' WITH "+config.user_sid+" IN "+item_old)
        if "%%users.username%%" in item:
            item = item.replace("%%users.username%%", config.user_target)
            self.log_buddy.write_log("Execution","REPLACED '%%users.username%%' WITH "+config.user_target+" IN "+item_old)
        if "%%users.temp%%" in item:
            item = item.replace("%%users.temp%%", config.user_temp_dir+"\Temp")
            self.log_buddy.write_log("Execution","REPLACED '%%users.temp%%' WITH "+config.user_temp_dir+" IN "+item_old)
        if "%%users.localappdata%%" in item:
            item = item.replace("%%users.localappdata%%", config.user_local_appdata_dir)
            self.log_buddy.write_log("Execution","REPLACED '%%users.localappdata%%' WITH "+config.user_local_appdata_dir+" IN "+item_old)
        if "%%users.appdata%%" in item:
            item = item.replace("%%users.appdata%%", config.user_appdata_dir)
            self.log_buddy.write_log("Execution","REPLACED '%%users.appdata%%' WITH "+config.user_appdata_dir+" IN "+item_old)
        if "%%environ_systemroot%%" in item:
            item = item.replace("%%environ_systemroot%%", config.system_root+":\Windows")
            self.log_buddy.write_log("Execution","REPLACED '%%environ_systemroot%%' WITH "+config.system_root+" IN "+item_old)
        if "%%environ_systemdrive%%" in item:
            item = item.replace("%%environ_systemdrive%%", config.system_root+":\\")
            self.log_buddy.write_log("Execution","REPLACED '%%environ_systemdrive%%' WITH "+config.system_root+":\\ IN "+item_old)
        if ("%%environ_windir%%" in item) and (config.win_def == 0):
            item = item.replace("%%environ_windir%%", config.win_dir)
            self.log_buddy.write_log("Execution","REPLACED '%%environ_windir%%' WITH "+config.win_dir+" IN "+item_old)
        elif ("%%environ_windir%%" in item) and (config.win_def == 1):
            item = item.replace("%%environ_windir%%", config.system_root+":\Windows")
            self.log_buddy.write_log("Execution","REPLACED '%%environ_windir%%' WITH "+config.system_root+":\Windows IN "+item_old)
        if "%%environ_allusersappdata%%" in item:
            item = item.replace("%%environ_allusersappdata%%", config.system_root+":\ProgramData")
            self.log_buddy.write_log("Execution","REPLACED '%%environ_allusersappdata%%' WITH "+config.system_root+":\ProgramData IN "+item_old)
        if "%%environ_programfiles%%" in item:
            item = item.replace("%%environ_programfiles%%", config.system_root+":\Program Files")
            self.log_buddy.write_log("Execution","REPLACED '%%environ_programfiles%%' WITH "+config.system_root+":\Program Files IN "+item_old)
        if "%%environ_programfilesx86%%" in item:
            item = item.replace("%%environ_programfilesx86%%", config.system_root+":\Program Files (x86)")
            self.log_buddy.write_log("Execution","REPLACED '%%environ_programfilesx86%%' WITH "+config.system_root+":\Program Files (x86) IN "+item_old)
        if "%%users.homedir%%" in item:
            item = item.replace("%%users.homedir%%", config.user_path+"\\")
            self.log_buddy.write_log("Execution","REPLACED '%%users.homedir%%' WITH "+config.user_path+"\ IN "+item_old)
        if "%%environ_allusersprofile%%" in item:
            item = item #To Do for ALL USER case
        if r"\\\\" in item:
            item = item.replace(r"\\\\", r"\\")
            self.log_buddy.write_log("Execution","REPLACED \\ WITH \ IN "+item)
        return item

    def wmi_replacer(self, query):
        query_old = query
        if "ComputerSystem" in query:
            query = query.replace("ComputerSystemProduct", "ComputerSystem")
            self.log_buddy.write_log("Execution","REPLACED 'ComputerSystemProduct' WITH 'ComputerSystem' IN "+query_old)
        if "SystemDriver" in query:
            query = query.replace("SystemDriver", "SysDriver")
            query = query.replace("SELECT DisplayName, Description, InstallDate, Name, PathName, Status, State, ServiceType from","")
            query = query.replace("get *", "get DisplayName, Description, InstallDate, Name, PathName, Status, State, ServiceType")
            self.log_buddy.write_log("Execution","REPLACED 'SystemDriver' WITH 'SysDriver' IN "+query_old)
            self.log_buddy.write_log("Execution","REPLACED 'SELECT DisplayName, Description, InstallDate, Name, PathName, Status, State, ServiceType from' WITH '' IN "+query_old)
            self.log_buddy.write_log("Execution","REPLACED 'get *' WITH get 'DisplayName, Description, InstallDate, Name, PathName, Status, State, ServiceType' IN "+query_old)
        if "from Product get" in query:
            query = query.replace("SELECT Name, Vendor, Description, InstallDate, InstallDate2, Version from", "")
            query = query.replace("get *","get Name, Vendor, Description, InstallDate, InstallDate2, Version")
            self.log_buddy.write_log("Execution","REPLACED 'SELECT Name, Vendor, Description, InstallDate, InstallDate2, Version from' WITH '' IN "+query_old)
            self.log_buddy.write_log("Execution","REPLACED 'get *' WITH 'get Name, Vendor, Description, InstallDate, InstallDate2, Version' IN "+query_old)
        if "LastBootUpTime" in query:
            query = query.replace("SELECT LastBootUpTime FROM","")
            query = query.replace("get *","get LastBootUpTime")
            self.log_buddy.write_log("Execution","REPLACED 'SELECT LastBootUpTime FROM' WITH '' IN "+query_old)
            self.log_buddy.write_log("Execution","REPLACED 'get *' WITH 'get LastBootUpTime' IN "+query_old)
        if "QuickFixEngineering" in query:
            query = query.replace("QuickFixEngineering", "QFE")
            self.log_buddy.write_log("Execution","REPLACED 'QuickFixEngineering' WITH 'QFE' IN "+query_old)
        if "OperatingSystem" in query:
            query = query.replace("OperatingSystem","OS")
            self.log_buddy.write_log("Execution","REPLACED 'OperatingSystem' WITH 'OS' IN "+query_old)
        if "LogonSession" in query:
            query = query.replace("LogonSession","Logon")
            self.log_buddy.write_log("Execution","REPLACED 'LogonSession' WITH 'Logon' IN "+query_old)
        if "GroupUser" in query:
            query = query.replace("GroupUser where Name = \"login_users\"", "Group")
            self.log_buddy.write_log("Execution","REPLACED 'GroupUser where Name = \"login_users\"' WITH 'Group' IN "+query_old)
        if "PhysicalMemory" in query:
            query = query.replace("PhysicalMemory","MEMPHYSICAL")
            self.log_buddy.write_log("Execution","REPLACED 'PhysicalMemory' WITH 'MEMPHYSICAL' IN "+query_old)
        if "UserProfile" in query:
            query = query.replace("UserProfile WHERE SID='%%users.sid%%'", "UserAccount")
            self.log_buddy.write_log("Execution","REPLACED 'UserProfile WHERE SID='%%users.sid%%' WITH 'UserAccount' IN "+query_old)
        if "StartupCommand" in query:
            query = query.replace("StartupCommand", "Startup")
            self.log_buddy.write_log("Execution","REPLACED 'StartupCommand' WITH 'Startup' IN "+query_old)
        query = query.replace(",",".") #Because CSV
        self.log_buddy.write_log("Execution","REPLACED ',' WITH '.' IN "+query_old)
        return query
