# Pathloss Version 4.0 File Association

The pathloss installation program did not complete the Windows registry entry correctly on shipments before August 1999. Double clicking on a pathloss file (pl4) would start the program but did not load the file. The procedure to edit the registry and correct this problem is given in the steps below.

Click Start - Run and enter the command line REGEDIT. Click OK to start the windows registry editor program.   
Select Edit - Find.. on the menu bar and enter the search string pl4file.

![](images/ab795687ea2189f2a3ec38d59988454bff34feaa072cd225ba69ce5aa24659b8.jpg)

<details>
<summary>text_image</summary>

Find
Find what: pl4file
Look at
Keys
Values
Data
Match whole string only
Find Next
Cancel
</details>

The correct location is shown in the directory structure on the right.

![](images/2e29a2fb142ab0d47113cc59d514a3c4e7b0d80a9a0446ad71355997ac76565d.jpg)

<details>
<summary>text_image</summary>

pl4file
DefaultIcon
Shell
Open
command
C:\PLW40\plw40.exe %1
</details>

Double click on the “ab” icon and edit the entry as shown. The %1 is the missing portion. The path name will be the directory that the pathloss program was installed in.   
Click OK and close REGEDIT program.

![](images/f5570cfad4440b36e377a399afa3dc6566fb837d4a848931c97355bb7489ce2e.jpg)

<details>
<summary>text_image</summary>

Edit String
Value name:
(Default)
Value data:
C:\PLW40\plw40.exe %1
OK	Cancel
</details>