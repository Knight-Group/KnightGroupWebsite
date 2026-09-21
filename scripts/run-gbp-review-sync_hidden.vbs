Option Explicit

Dim fsoFlag, shell, fso, root, ps1, pythonw, launcher, cmd

Set fsoFlag = CreateObject("Scripting.FileSystemObject")
If fsoFlag.FileExists("E:\STOP-FLASHES.flag") Then WScript.Quit 0
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = root

ps1 = root & "\run-gbp-review-sync.ps1"
pythonw = "C:\Users\nknig\AppData\Local\Programs\Python\Python312\pythonw.exe"
launcher = "E:\Experimental Autonomous AI Monkey Maker\scripts\run-ps-noconsole.py"
If fso.FileExists(pythonw) And fso.FileExists(launcher) Then
  cmd = """" & pythonw & """ """ & launcher & """ """ & ps1 & """"
  WScript.Quit shell.Run(cmd, 0, True)
End If

cmd = "powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File """ & ps1 & """"
WScript.Quit shell.Run(cmd, 0, True)
