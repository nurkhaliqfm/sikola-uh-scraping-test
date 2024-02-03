import xml.etree.ElementTree as ET

# Create the root element
rootXMLQuiz = ET.Element("quiz")

# Essay Format
mainBlocQustion = ET.SubElement(rootXMLQuiz, "question", type="essay")

name = ET.SubElement(mainBlocQustion, "name")
subText = ET.SubElement(name, "text")
subText.text = "ESSAYQUESTION"

question = ET.SubElement(mainBlocQustion, "questiontext", format="html")
subText = ET.SubElement(question, "text")
subText.text = "Isi Soal"

generalfeedback = ET.SubElement(mainBlocQustion, "generalfeedback", format="html")
subText = ET.SubElement(generalfeedback, "text")

defaultgrade = ET.SubElement(mainBlocQustion, "defaultgrade")
defaultgrade.text = "10"

penalty = ET.SubElement(mainBlocQustion, "penalty")
penalty.text = "0"

hidden = ET.SubElement(mainBlocQustion, "hidden")
hidden.text = "0"

idnumber = ET.SubElement(mainBlocQustion, "idnumber")
idnumber.text = "idNumber-x-x-x"

responseformat = ET.SubElement(mainBlocQustion, "responseformat")
responseformat.text = "editor"

responserequired = ET.SubElement(mainBlocQustion, "responserequired")
responserequired.text = "1"

responsefieldlines = ET.SubElement(mainBlocQustion, "responsefieldlines")
responsefieldlines.text = "10"

minwordlimit = ET.SubElement(mainBlocQustion, "minwordlimit")
maxwordlimit = ET.SubElement(mainBlocQustion, "maxwordlimit")

attachments = ET.SubElement(mainBlocQustion, "attachments")
attachments.text = "0"

attachmentsrequired = ET.SubElement(mainBlocQustion, "attachmentsrequired")
attachmentsrequired.text = "0"

maxbytes = ET.SubElement(mainBlocQustion, "maxbytes")
maxbytes.text = "0"

filetypeslist = ET.SubElement(mainBlocQustion, "filetypeslist")

graderinfo = ET.SubElement(mainBlocQustion, "graderinfo", format="html")
subText = ET.SubElement(graderinfo, "text")

responsetemplate = ET.SubElement(mainBlocQustion, "responsetemplate", format="html")
subText = ET.SubElement(responsetemplate, "text")


essayxml = ET.ElementTree(rootXMLQuiz)

# Write the XML to a file
essayxml.write("quiz.xml", encoding="utf-8", xml_declaration=True)
