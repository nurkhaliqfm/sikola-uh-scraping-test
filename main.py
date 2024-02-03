from bs4 import BeautifulSoup
import html
import glob
import os
import lxml.etree as ET


listScrapingResultFile = glob.glob(f"data/quiz/*.xml")
quizTypeList = []
for filePath in listScrapingResultFile:
    fileName = filePath.split("/")[2]
    # print(fileName)
    
    if not os.path.exists(f"data/quiz-converted/{fileName}"):
        # Create the root element for XML
        rootXMLQuiz = ET.Element("quiz")
        
        with open(filePath, "r") as f:
            data = f.read()
        bs_data = BeautifulSoup(data, "xml")

        # Quiz Name & Code
        quizName = bs_data.find("section").get("title")

        # Quiz Question
        for attrQuest in bs_data.find_all("assessmentItem"):
            # Question
            if attrQuest.find("prompt") != None:
                quizMainQuestion = ET.CDATA(f"<p>{html.unescape(attrQuest.get("title"))}</p>{html.unescape(attrQuest.find("prompt").text.strip())}")
            else:
                quizMainQuestion = ET.CDATA(f"<p>{html.unescape(attrQuest.get("title"))}</p>")
                
            # Question Answare Attributes
            quizChoiceAnswerType = attrQuest.find('responseDeclaration').get('cardinality')
            quizChoiceAnswerBaseType = attrQuest.find('responseDeclaration').get('baseType')
            quizCode = attrQuest.find('responseDeclaration').get('identifier')

            # SingleChoice Format
            if quizChoiceAnswerBaseType == 'identifier' and quizChoiceAnswerType == 'single':
                mainBlocQustion = ET.SubElement(rootXMLQuiz, "question", type="multichoice")
                name = ET.SubElement(mainBlocQustion, "name")
                subText = ET.SubElement(name, "text")
                subText.text = quizName

                question = ET.SubElement(mainBlocQustion, "questiontext", format="html")
                subText = ET.SubElement(question, "text")
                subText.text = quizMainQuestion

                generalfeedback = ET.SubElement(mainBlocQustion, "generalfeedback", format="html")
                subText = ET.SubElement(generalfeedback, "text")

                defaultgrade = ET.SubElement(mainBlocQustion, "defaultgrade")
                defaultgrade.text = '1'

                penalty = ET.SubElement(mainBlocQustion, "penalty")
                penalty.text = "0"

                hidden = ET.SubElement(mainBlocQustion, "hidden")
                hidden.text = "0"
                
                idnumber = ET.SubElement(mainBlocQustion, "idnumber")
                idnumber.text = quizCode

                single = ET.SubElement(mainBlocQustion, "single")
                single.text = 'true'
                
                answernumbering = ET.SubElement(mainBlocQustion, "answernumbering")
                answernumbering.text = 'abc'
                
                showstandardinstruction = ET.SubElement(mainBlocQustion, "showstandardinstruction")
                showstandardinstruction.text = "0"

                correctfeedback = ET.SubElement(mainBlocQustion, "correctfeedback", format='html')
                subText = ET.SubElement(correctfeedback, "text")
                subText.text = ET.CDATA("<p>Your answer is correct.</p>")
                
                partiallycorrectfeedback = ET.SubElement(mainBlocQustion, "partiallycorrectfeedback", format='html')
                subText = ET.SubElement(partiallycorrectfeedback, "text")
                subText.text = ET.CDATA("<p>Your answer is partially correct.</p>")
                
                incorrectfeedback = ET.SubElement(mainBlocQustion, "incorrectfeedback", format='html')
                subText = ET.SubElement(incorrectfeedback, "text")
                subText.text = ET.CDATA("<p>Your answer is incorrect.</p>")

                shownumcorrect = ET.SubElement(mainBlocQustion, "shownumcorrect")

                for choices in attrQuest.find_all('simpleChoice'):
                    if choices.find('feedbackInline') != None:
                        quesChoiceFeedbackText = ET.CDATA(html.unescape(choices.find('feedbackInline').text.strip()))
                        quesChoiceText = choices.find('feedbackInline').decompose()
                    
                    quesChoiceText = ET.CDATA(html.unescape(choices.text.strip()))
                    choicesTrueName = choices.get('identifier')
                    quizChoicePoint = f"{float(attrQuest.find('mapEntry', {'mapKey':choicesTrueName}).get('mappedValue'))*10}"
                    
                    answer = ET.SubElement(mainBlocQustion, "answer", fraction=quizChoicePoint, format="html")
                    subText = ET.SubElement(answer, "text")
                    subText.text = quesChoiceText
                    feedback = ET.SubElement(answer, "feedback")
                    feedbackText = ET.SubElement(feedback, "text")
                    if choices.find('feedbackInline') != None:
                        feedbackText.text = quesChoiceFeedbackText
                
            # MultipleChoice Format
            elif quizChoiceAnswerBaseType == 'identifier' and quizChoiceAnswerType == 'multiple':
                    mainBlocQustion = ET.SubElement(rootXMLQuiz, "question", type="multichoice")
                    name = ET.SubElement(mainBlocQustion, "name")
                    subText = ET.SubElement(name, "text")
                    subText.text = quizName

                    question = ET.SubElement(mainBlocQustion, "questiontext", format="html")
                    subText = ET.SubElement(question, "text")
                    subText.text = quizMainQuestion

                    generalfeedback = ET.SubElement(mainBlocQustion, "generalfeedback", format="html")
                    subText = ET.SubElement(generalfeedback, "text")

                    defaultgrade = ET.SubElement(mainBlocQustion, "defaultgrade")
                    defaultgrade.text = '1'

                    penalty = ET.SubElement(mainBlocQustion, "penalty")
                    penalty.text = "0"

                    hidden = ET.SubElement(mainBlocQustion, "hidden")
                    hidden.text = "0"
                    
                    idnumber = ET.SubElement(mainBlocQustion, "idnumber")
                    idnumber.text = quizCode

                    single = ET.SubElement(mainBlocQustion, "single")
                    single.text = 'false'
                    
                    answernumbering = ET.SubElement(mainBlocQustion, "answernumbering")
                    answernumbering.text = 'abc'
                    
                    showstandardinstruction = ET.SubElement(mainBlocQustion, "showstandardinstruction")
                    showstandardinstruction.text = "0"

                    correctfeedback = ET.SubElement(mainBlocQustion, "correctfeedback")
                    subText = ET.SubElement(correctfeedback, "text")
                    subText.text = ET.CDATA("<p>Your answer is correct.</p>")
                    
                    partiallycorrectfeedback = ET.SubElement(mainBlocQustion, "partiallycorrectfeedback")
                    subText = ET.SubElement(partiallycorrectfeedback, "text")
                    subText.text = ET.CDATA("<p>Your answer is partially correct.</p>")
                    
                    incorrectfeedback = ET.SubElement(mainBlocQustion, "incorrectfeedback")
                    subText = ET.SubElement(incorrectfeedback, "text")
                    subText.text = ET.CDATA("<p>Your answer is incorrect.</p>")

                    shownumcorrect = ET.SubElement(mainBlocQustion, "shownumcorrect")

                    for choices in attrQuest.find_all('simpleChoice'):
                        if choices.find('feedbackInline') != None:
                            quesChoiceFeedbackText = ET.CDATA(html.unescape(choices.find('feedbackInline').text.strip()))
                            quesChoiceText = choices.find('feedbackInline').decompose()
                        
                        quesChoiceText = ET.CDATA(html.unescape(choices.text.strip()))
                        choicesTrueName = choices.get('identifier')
                        quizChoicePoint = f"{float(attrQuest.find('mapEntry', {'mapKey':choicesTrueName}).get('mappedValue'))*10}"
                        
                        answer = ET.SubElement(mainBlocQustion, "answer", fraction=quizChoicePoint, format="html")
                        subText = ET.SubElement(answer, "text")
                        subText.text = quesChoiceText
                        feedback = ET.SubElement(answer, "feedback")
                        feedbackText = ET.SubElement(feedback, "text")
                        if choices.find('feedbackInline') != None:
                            feedbackText.text = quesChoiceFeedbackText
                    
            # Essay Format
            elif quizChoiceAnswerBaseType == 'string':
                    quizTruePoint = attrQuest.find('defaultValue').find('value').text

                    mainBlocQustion = ET.SubElement(rootXMLQuiz, "question", type="essay")
                    name = ET.SubElement(mainBlocQustion, "name")
                    subText = ET.SubElement(name, "text")
                    subText.text = quizName

                    question = ET.SubElement(mainBlocQustion, "questiontext", format="html")
                    subText = ET.SubElement(question, "text")
                    subText.text = quizMainQuestion

                    generalfeedback = ET.SubElement(mainBlocQustion, "generalfeedback", format="html")
                    subText = ET.SubElement(generalfeedback, "text")

                    defaultgrade = ET.SubElement(mainBlocQustion, "defaultgrade")
                    defaultgrade.text = f"{float(quizTruePoint)*10}"

                    penalty = ET.SubElement(mainBlocQustion, "penalty")
                    penalty.text = "0"

                    hidden = ET.SubElement(mainBlocQustion, "hidden")
                    hidden.text = "0"

                    idnumber = ET.SubElement(mainBlocQustion, "idnumber")
                    idnumber.text = quizCode

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



        # Write the XML to a file
        quizXMLGenerate = ET.ElementTree(rootXMLQuiz)
        quizXMLGenerate.write(f"data/quiz-converted/{fileName}", encoding="utf-8", xml_declaration=True)

