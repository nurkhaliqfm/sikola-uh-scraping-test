from bs4 import BeautifulSoup
import html
import pandas as pd

with open("data/test/qti2export_7013.xml", "r") as f:
    data = f.read()
bs_data = BeautifulSoup(data, "xml")

# Quiz Name & Code
quizCode = bs_data.find("section").get("ident")
quizName = bs_data.find("section").get("title")

# Quiz Question
allQuestionData = []
for attrQuest in bs_data.find_all("assessmentItem"):
    questionData=[]
    # Question
    quizMainQuestion = f"<![CDATA[<p>{attrQuest.get("title")}</p>{html.unescape(attrQuest.find("prompt").text.strip())}]]>"
    
    # Question Choice
    questChoices = []
    for choices in attrQuest.find_all('simpleChoice'):
        questChoices.append(f"<![CDATA[{html.unescape(choices.text.strip())}]]>")
        
    # Question Answare
    quizChoiceAnswerType = attrQuest.find('responseDeclaration').get('cardinality')
    quizTrueAnswer = attrQuest.find('correctResponse').find('value').text
    quizTruePoint = attrQuest.find('mapEntry', {'mapKey':quizTrueAnswer}).get('mappedValue')

    questionData.append(quizMainQuestion)
    questionData.append(questChoices)
    questionData.append(quizChoiceAnswerType)
    questionData.append(quizTrueAnswer)
    questionData.append(quizTruePoint)
    
    allQuestionData.append(questionData)
    
print(allQuestionData)
