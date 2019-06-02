
    _    _  ___  ____________ 
   | |  | |/ _ \ | ___ \  _  \
   | |  | / /_\ \| |_/ / | | |
   | |/\| |  _  ||    /| | | |
   \  /\  / | | || |\ \| |/ / 
    \/  \/\_| |_/\_| \_|___/  
    
     _       _____    ____  ____ 
| |     / /   |  / __ \/ __ \
| | /| / / /| | / /_/ / / / /
| |/ |/ / ___ |/ _, _/ /_/ / 
|__/|__/_/  |_/_/ |_/_____/  
                             
                           
                           
# WARD
Windows Artifact Retrieval and Discovery

Usage:

  -t (Target) - Specify remote hostname/IP Address
  
  -c (Credential) - Specify credential of elevated user with Remote WMI Access to Target
  
  -u (User Target) - Specify User Target on Remote Host, will add userless option to collect ALL local user data
  
  -a (Admin?) - Toggle for running from Elevated User Prompt on local PC to avoid password prompting and use more local functionality
  
  
Relies on Windows Artifact listing from https://github.com/ForensicArtifacts/artifacts, included under /yamldata directory.

WARD is intended for usage on enterprise domains where machines will typically have WMI or WINRM enabled.  It should be run either from an elevated terminal or be provided with administrator user credentials at execution in order to function properly.  WMI is used to execute commands on the remote host for as few as possible, with file copies done after drive mapping and WMIC used locally to pull data where accessible.  Execution and Error logs are created in order to track progress of program execution.

Log/Data folders are output in the format 'TARGETMACHINE'[TARGETUSER]'.  A target user is currently expected in order to narrow the scope of results but a switch will be added to process ALL users with active profiles on the machine in the future.


DEPENDENCIES
-YAML - For reading input data.
-TQDM - Pretty Progress Bars.
-COLORAMA - Might remove, was used to help implement TQDM
-WMI - Implement Windows Management Instrumentation functionality in native Python
-PyWin32
-ArgParse
