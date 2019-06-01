# WARD
Windows Artifact Retrieval and Discovery

Usage:
  -t (Target) - Specify remote hostname/IP Address
  -c (Credential) - Specify credential of elevated user with Remote WMI Access to Target
  -u (User Target) - Specify User Target on Remote Host, will add userless option to collect ALL local user data
  -a (Admin?) - Toggle for running from Elevated User Prompt on local PC to avoid password prompting and use more local functionality
  
Relies on Windows Artifact listing from https://github.com/ForensicArtifacts/artifacts - Working on adding proper YAML support to allow real-time download/interpretation, this was a trial run.
