
import wmi, subprocess
session = wmi.WMI(computer="DESKTOP-2C3IQHO", user="testing", password="testing")
#SW_SHOWNORMAL = 1
process_startup = session.Win32_ProcessStartup.new()
path = "C:\\Users\\testing\WMIUsers0.txt"
#path = "\""+path+"\""
#process_startup.ShowWindow = SW_SHOWNORMAL
#command = "\"C:\WINDOWS\system32\cmd.exe\" /c wmic /output:"+path+" /namespace:\\root\cimv2 UserAccount get * /value"

#command = r"cmd /K wmic /namespace:\root\cimv2 UserAccount get * /value > C:\Users\testing\WMIUsers0.txt"
#command = command.replace('wmic', "\"wmic")
#command = command.replace(".txt",".txt\"")
#command = command.replace("cmd", "\"C:\WINDOWS\system32\cmd.exe\"")
#command=r"cmd.exe /c ipconfig /all > C:\Users\testing\ipconfig.txt"
#process_id, return_value = session.Win32_Process.Create(CommandLine=command, ProcessStartupInformation=process_startup)




command = "wmic /node:\"DESKTOP-2C3IQHO\" /user:testing /password:testing os get name > C:\\Users\Joe\WMI.txt" 
#result = subprocess.run(command, shell=True)
#result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=10)
result = subprocess.getoutput(command)
print(result)
#with open(r"C:\Users\Joe\WMI.txt", 'w') as f:
#    f.write("OS NAME\n")
#    f.write(result)
    #f.write(result.stdout)
    #f.write(result.stdout.decode('utf-8'))
    #f.write(result.stderr.decode('utf-8'))
print("Process Executed: "+command)
#print("Process ID: "+str(process_id)+" , Return Value (0 = Success): "+str(return_value)+"\n")


