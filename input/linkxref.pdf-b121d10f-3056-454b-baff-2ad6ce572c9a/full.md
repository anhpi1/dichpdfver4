# IMPORT LINK TEXT FILES

# PATHLOSS RADIO AND ANTENNA FILES CROSS REFERENCE

A radio and antenna data files cross reference has been added to the Import link text files operation. This feature allows an interference calculation to be carried out immediately following the import. External text files are used to cross reference the radio and antenna identifiers used in the import data to the Pathloss radio and antenna code files.

The Pathloss code files are used to fill in any missing information in the import data. For example if the import data contains only the transmit power and the radio identifier, the receiver threshold information would be read from the cross referenced Pathloss radio code file, but the transmit power would not be changed.

The cross reference files are ASCII text files which meet the following requirements:

• The file names must be “ant\_xref.txt” and “rad\_xref.txt” for the antennas and radios cross reference files respectively. These files must be located in the same directory that the Pathloss program is installed in.   
• Each line in the file must consist of the import data descriptor in double quotes followed by the Pathloss code file name separated by a space or tab.   
The comparison in the cross reference is not case sensitive; however the spelling in the cross reference file must be the same as the data file. If there are several variants in the import data file, then a cross reference line must be created for each variant. The same Pathloss code file name could be used for each variant.

An example of a radio and antenna cross reference file is given below.

ant\_xref.txt

"15\_GHz/0.6m Andrew" 6962   
"15\_GHz/1.2m Andrew" 6964   
"15\_GHz/0.3m Andrew" 6961   
"18\_GHz/0.6m ANDREW" 6967   
"18\_GHz/0.3m ANDREW" 7010   
"18\_Ghz/1.2m ANDREW" 4504a

rad\_xref.txt

"Ajax radio AJ15, 8x2 guaranteed" AJ15\_16s\_8E1

"Ajax radio AJ15, 4x2 guaranteed" AJ15\_4s\_4E1

"Ajax radio AJ15, 16x2 guaranteed" AJ15\_16s\_16E1

"Ajax radio AJ18, 8x2 guaranteed" AJ18\_16s\_8E1

"Ajax radio AJ18, 4x2 guaranteed" AJ18\_4s\_4E1

"Ajax radio AJ18, 16x2 guaranteed" AJ18\_16s\_16E1

The radio and antenna data files must be available for the conversion to succeed. The location of the files must be identified. Click Configure - Directories - Microwave Antenna Codes / Microwave Radio Codes and point to the top most directory which contains the data files