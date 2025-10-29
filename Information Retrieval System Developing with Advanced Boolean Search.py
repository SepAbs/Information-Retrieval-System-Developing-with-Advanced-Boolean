import nltk
from nltk.tokenize import wordpunct_tokenize
nltk.download('stopwords')
from nltk.corpus import stopwords
from random import choice
from math import sqrt

def preProcessor(String):
    String = wordpunct_tokenize(String.replace(".", "").lower()) #Case Folding & Tokenisations
    null, Consonants, Irregulars, stopWords = "", "qwrtypsdfghjklzxcvbnm", {"children":"child", "feet":"foot", "teeth": "tooth", "mice": "mouse", "people": "person"}, stopwords.words('english')

    for Index in range(len(String)):
        if String[Index] in stopWords: #Stop Words Elimination
            String[Index] = null
            
        #Asymmetric Expansion
        elif String[Index][-3:] == "ies" and String[Index][-4] in Consonants:
            String[Index] = String[Index][:-3] + "y"

        elif String[Index][-3:] == "ves":
            String[Index] = String[Index][:-3] + "f"
            
        elif String[Index][-2:] == "es" and (String[Index][-3] in ["s", "x", "z"] or String[Index][-4:-2] in ["ch, sh"] or (String[Index][-3] == "o" and String[Index][-4] in Consonants)):
            String[Index] = String[Index][:-2]
        
        elif String[Index][-1] == "s":
            String[Index] = String[Index][:-1]
            
        elif String[Index][-3:] == "men":
            String[Index] = String[Index][:-3] + "man"
        
        elif String[Index] in Irregulars.keys():
            String[Index] = Irregulars[String[Index]]
        
    while null in String:
            String.remove(null)      
    return String

def And(Query):
    Query = preProcessor(Query.replace(" and ", " "))
    ID1, ID2 = InvertedIndexStruct[Query[0]], InvertedIndexStruct[Query[1]]
    if ID1[-1] < ID2[0] or ID2[-1] < ID1[0] or any(Q not in InvertedIndexStruct for Q in Query):
        return []  

    lengthD1, lengthD2 = len(ID1), len(ID2)
    AND, Skip1, Skip2, Index1, Index2 = [], int(sqrt(lengthD1)), int(sqrt(lengthD1)), 0, 0  #Start semi-optimizing by assinging skip accumulator for the first postingslist.

    while Index1 < lengthD1 and Index2 < lengthD2:
        if ID1[Index1] == ID2[Index2]:
            AND.append(ID2[Index2])
            Index1 += 1
            Index2 += 1

        elif ID1[Index1] >= ID2[Index2]:
            Index1 += Skip1
            Index2 += Skip2
            
        else:
            if Index1 + Skip1 < lengthD1 and ID1[Index1 + Skip1] <= ID2[Index2]:
                while Index1 + Skip1 < lengthD1 and ID1[Index1 + Skip1] <= ID2[Index2]:
                    Index1 += Skip1
                else:
                    Index1 += 1
                    
            elif Index2 + Skip2 < lengthD2 and ID2[Index2 + Skip2] <= ID2[Index2]:
                while Index2 + Skip2 < lengthD1 and ID1[Index2 + Skip2] <= ID1[Index1]:
                    Index2 += Skip2
                else:
                    Index2 += 1
    return AND
        
def Not(Query):
    Query = preProcessor(Query.replace(" not ", " "))
    if Query[0] not in InvertedIndexStruct:
        return []

    NOT = []
    ID1, ID2 = InvertedIndexStruct[Query[0]], InvertedIndexStruct[Query[1]]
    for ID in ID1:
        if ID not in ID2:
            NOT.append(ID)
    return sorted(NOT)
    
def Or(Query):
    Query = preProcessor(Query.replace(" or ", " "))
    if all(Q not in InvertedIndexStruct for Q in Query):
        return []
    
    for Q in Query:
        QID = InvertedIndexStruct[Q]
        if len(QID) == lengthDocs:
            return QID
        
    OR = []
    for Q in Query:
        if Q in InvertedIndexStruct:
            OR += InvertedIndexStruct[Q]
    return sorted(set(OR))

def Proximity(Query):
    String = f" near/{Query.split()[1][-1]} "
    Query = preProcessor(Query.replace(String, " "))
    Q0, Q1 = Query[0], Query[1]
    ID1, ID2 = InvertedIndexStruct[Q0], InvertedIndexStruct[Q1]
    if ID2[-1] < ID1[0] or ID1[-1] < ID2[0] or any(Q not in InvertedIndexStruct for Q in Query):
        return []
    
    PROX = []
    for ID in ID1:
        if ID in ID2:
            PROX.append(ID)
    
    Proximity = []
    for Element in PROX:
        File = open(listDocs[Element - 1], "r")
        Location = preProcessor(File.read())
        if abs(Location.index(Q0) - Location.index(Q1)) <= int(String[-2]):
            Proximity.append(Element)
        File.close()
    return sorted(Proximity)

def Main(Query):
    if " and " in Query:
        return And(Query)
    
    elif " not " in Query:
        return Not(Query)
                
    elif " or " in Query:
        return Or(Query)
    
    return Proximity(Query) #The stop words are ignored.

#Globals!
listDocs, lengthDocs = [], 0

while True:
    try:
        while True:
            Document = input("Enter your text document: ")
            if ".txt" == Document[-4:].lower() and Document not in listDocs:
                break
        listDocs.append(Document)
        lengthDocs += 1
        
    except EOFError: #Enter Ctrl+d to exit
        print("START!")
        print()
        break
    
InvertedIndexStruct = dict()
for Index in range(1,8):
    Lines, File = [], open(f"{Index}.txt", "r")
    for Line in File:
        if Line != "\n":
            Lines += preProcessor(Line)

    if Lines != []:
        Lines = sorted(Lines)
        for Term in Lines:
            I = Index + 1
            if Term in InvertedIndexStruct and I not in InvertedIndexStruct[Term]:
                InvertedIndexStruct[Term].append(I)
            else:
                InvertedIndexStruct[Term] = [I]
    File.close()

InvertedIndexStruct = dict(sorted(InvertedIndexStruct.items()))
print("Term-Document Inverted Index Structure:")
print()
print(InvertedIndexStruct)
print()

while True:
    Query = input("What are you looking for? ").lower()
    BooList = [" not ", " and ", " or ", " near/"] #As the default, promixity has the least priority.
    while all(BOO not in Query for BOO in BooList):
        Query = input("What are you looking for? Boolean or proximity please. ").lower()

    print(Main(Query)) #Main is ready to be called.
    
    End = input("Wanna end this? <Y, N> ")
    while End not in ["Y", "y", "N", "n"]:
        End = input("DON'T WASTE MY TIME! You wanna end this? <Y, N> ")
    if End in "Yy":
        print("Good-bye")
        break
    else:
        print("Goodluck!")
        print()
