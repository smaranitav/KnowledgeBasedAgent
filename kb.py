import re
import time

class Predicate:
    def __init__(self, predicate, negation, arguments, sentence_number):
        self.predicate = predicate
        self.negation = negation
        self.arguments = arguments
        self.sentence_number = sentence_number

def processInputFile(file):
    input_list=[]
    for inputs in open(file):
        input_list.append(inputs.rstrip('\n'))

    global num_queries
    num_queries=int(input_list[0])

    global query_sentences
    query_sentences=[]

    for i in range(num_queries):
        query_sentences.append(input_list[i+1])

    global num_sentences
    num_sentences =int(input_list[num_queries+1])

    global sentences
    sentences=[]

    cur_index=2+num_queries
    for i in range(num_sentences):
        sentences.append(input_list[cur_index+i])

    
def convertToCNF(sentences):
    
    global cnf_statements
    cnf_statements=[]

    for i in range(len(sentences)):
        cnf_statement=[]
        #to remove any spaces between words
        sentence = sentences[i].replace(" ","")
        #Implication elimination step
        if sentence.find("=>"):
            implication_eliminated=sentence.split("=>")
            #print("implication_eliminated", implication_eliminated)
            for j in range(len(implication_eliminated)-1):
                if implication_eliminated[j].find("&"):
                    and_eliminated=implication_eliminated[j].split("&")
                    #print("and elimination", and_eliminated)
                    for k in range(len(and_eliminated)):
                        if and_eliminated[k][0]=="~":#if literal is negated
                            and_eliminated[k]=and_eliminated[k][1:]
                            cnf_statement.append(and_eliminated[k])
                        else:
                            cnf_statement.append("~"+and_eliminated[k])
                else:
                    if implication_eliminated[j][0]=="~":
                        implication_eliminated[j]=implication_eliminated[j][1:]
                        cnf_statement.append(implication_eliminated[j])
                    else:
                        cnf_statement.append("~"+implication_eliminated[j])
            cnf_statement.append(implication_eliminated[-1])
        cnf_statements.append(cnf_statement)

def checkIfArgsSame(arg_li1, arg_li2):
    same=True
    if len(arg_li2)==len(arg_li1):
        for i in range(len(arg_li1)):
            if arg_li1[i]!=arg_li2[i]:
                same=False
                break
    else:
        same= False
    return same

def checkIfAlreadyInKB(clause_li):
    #iterate through all clauses of kb to see if the current clause exists
    #holds the list of True/false to see if sentence in kb is there
    li=[]
    for i in range(len(temp_kb)):
        #changed
        present= True
        cur_clause = temp_kb[i]
        cur_clause_length =len(cur_clause)
        if cur_clause_length == len(clause_li):
            
            for j in range(len(clause_li)):
                for k in range(len(cur_clause)):
                    #if present in kb
                    if cur_clause[k].predicate == clause_li[j].predicate and cur_clause[k].negation == clause_li[j].negation:
                        if checkIfArgsSame(cur_clause[k].arguments,clause_li[j].arguments):
                            continue
                        else:
                            present = False
                            break
                    #if not present in kb
                    else:
                        present= False
                        break
                if(not present):
                    break
            if present:
                li.append(1)
            else:
                li.append(0)
        else:
            li.append(0)
    li.sort()
    #print(li)
    if li[-1]==1:
        return True
    else:
        return False

def unify_args(arg_li1, arg_li2):
    if len(arg_li1)== len(arg_li2):
        for i in range(len(arg_li1)):
            a=arg_li1[i]
            b=arg_li2[i]

            if(a==b):
                continue
            else:
                if(isVariable(a) and isConstant(b)):
                    continue
                elif(isConstant(a) and isVariable(b)):
                    continue
                elif(isConstant(a) and isConstant(b)): #both are constants and different means cant be unified
                    return False
        return True
    else:
        return False
#del
def checkIfFactoringIsPossible(pred_a, pred_b, args_a, args_b, neg_a, neg_b):
    if (pred_a == pred_b and ((not neg_a and neg_b) or (not neg_b and neg_a))):
        if checkIfArgsSame(args_a, args_b):
            return True
    return False

#todo
def get_factored_clause(clause_li):
    length= len(clause_li)
    new_li=[]
    for s in range(length):
        term_a = clause_li[s]
        pred_a=term_a.predicate
        args_a=term_a.arguments
        negation_a=term_a.negation

        for t in range(s+1,length):
            term_b = clause_li[t]
            pred_b=term_b.predicate
            args_b=term_b.arguments
            negation_b=term_b.negation
            
            if not checkIfFactoringIsPossible(pred_a, pred_b, args_a, args_b, negation_a, negation_b):
                if term_a not in new_li:
                    new_li.append(term_a)
                if term_b not in new_li:
                    new_li.append(term_b)
                
    if len(new_li)==0:
        return clause_li
    else:
        return new_li
def checkIfNegatedQueryInKB(clause_li):
    #iterate through all clauses of kb to see if the current clause exists
    #holds the list of True/false to see if sentence in kb is there
    #print("Checking if negated single literal is in kb")
    li=[]
    for i in range(len(temp_kb)):
        cur_clause = temp_kb[i]
        cur_clause_length =len(cur_clause)
        #i.e if length is 1
        if cur_clause_length == len(clause_li):
            present = True
            
            if cur_clause[0].predicate == clause_li[0].predicate: #predicates are equal
                if cur_clause[0].negation != clause_li[0].negation: #negation are not equal
                    if checkIfArgsSame(cur_clause[0].arguments, clause_li[0].arguments):
                        return True
                    else: #try seeing if they unify
                        canUnify=unify_args(cur_clause[0].arguments, clause_li[0].arguments)
                        if canUnify:
                            return True
                        
    return False

def standardizeVariables(arguments_list, variable_count):
    var_dict={}
    
    for i in range(len(arguments_list)):
        #if the first character of each of arguments is uppercase, then constant, else variable
        arg = arguments_list[i] #arg holds all arguments of a predicate
        for j in range(len(arg)): #iterate through each argument of a predicate
            first_char=arg[j][0]
            if(first_char.isupper()): #if first letter is capital, it is a constant
                continue
            else:
                if arg[j] not in var_dict:
                    variable_count+=1
                    var_dict[arg[j]]="x"+str(variable_count)
                    arguments_list[i][j]="x"+str(variable_count)
                else:
                    arguments_list[i][j]=var_dict[arg[j]]

    
    return arguments_list, variable_count

def standardize(kb):
    global variable_count
    variable_count=0
    for i in range(len(kb)):
        clause=kb[i] #one list is one sentence in the kb.i,e one sentence is one clause because or-separated
        all_arguments=[] #holds all arguments in a clause/sentence for different predicates
        for j in range(len(clause)):
            all_arguments.append(clause[j].arguments)
    
        standardized_args, variable_count = standardizeVariables(all_arguments, variable_count)
        #print(standardized_args)
        for term in range(len(clause)):
            for arg in range(len(clause[term].arguments)):
                #print(clause[term].arguments[arg])
                #print(standardized_args[term][arg])
                clause[term].arguments[arg] = standardized_args[term][arg]

def createKB(cnf_statements):
    global kb
    kb=[]


    global clauseList
    global sentence_number_in_kb

    global predicate_dictionary
    predicate_dictionary={}

    for i in range(len(cnf_statements)):
        clause = cnf_statements[i] #['~Take(x,Warfarin)', '~Take(x,NSAIDs)']
        sentence_number_in_kb= i+1 #starts from 1

        clauseList=[]
        for i in range(len(clause)):
            literal=clause[i] #~Take(x,Warfarin)
            if (literal[0]=="~"):
                negation = True
                literal=literal[1:]
            else:
                negation = False

            open_index = -1
            close_index = -1
            for i in range(0, len(literal)):
                if literal[i]=="(":
                    open_index=i
                elif literal[i]==")":
                    close_index=i
            predicate = literal[0:open_index]
            arguments = literal[open_index+1:close_index].split(",")

            
            literal_object = Predicate(predicate, negation, arguments, sentence_number_in_kb)
            clauseList.append(literal_object)


            if negation:
                predicate = "~"+predicate
            #keeps a list of sentences where predicate or negated predicate appear
            if predicate in predicate_dictionary.keys():
                #this handles the case if the same predicate appears in a single sentence, then dont add the sentence number twice
                if sentence_number_in_kb not in predicate_dictionary[predicate]:
                    predicate_dictionary[predicate]+=[sentence_number_in_kb]

            else:
                
                predicate_dictionary[predicate]=[sentence_number_in_kb]
            
        kb.append(clauseList)

    #print("Knowledge base is", kb)
    #print("Predicate_dictionary is",predicate_dictionary)
    return sentence_number_in_kb

def addQueryToKB(query, query_num):
    clauseList=[]
    #print("query_num is", query_num)
    #initiallu, negation is true ~take
    if query[0]=="~":
        negation = True
        query=query[1:]
    else:
        negation = False
    
    open_index = -1
    close_index = -1
    for i in range(len(query)):
        if query[i]=="(":
            open_index=i
        elif query[i]==")":
            close_index=i
    #negating the query
    if negation: #suppose ~take in query, now change to take
        predicate = query[0:open_index]
        negation = False
        negated_predicate = predicate
    else:
        predicate =query[0:open_index]
        negation= True #new negation
        negated_predicate = "~"+predicate

    
    arguments = query[open_index+1:close_index].split(",")
        
    query_object = Predicate(predicate, negation, arguments, query_num)
    clauseList.append(query_object)
    temp_kb.append(clauseList)

    
    if negated_predicate in predicate_dictionary.keys():
        predicate_dictionary[negated_predicate]+=[query_num]
    else:
        predicate_dictionary[negated_predicate]=[query_num]
    
    query_list.append(query_num)

def isConstant(arg):
    if arg[0].isupper():
        return True
    else:
        return False

def isVariable(arg):
    if arg[0].islower():
        return True
    else:
        return False

def checkIfSame(c1, c2):
    if c1==c2:
        return True
    else:
        return False

def createCNFform(term):
    pred=term.predicate
    neg= term.negation
    args_li=term.arguments
    args=""
    for i in range(0, len(args_li)):
        if i==0:
            args=args_li[i]
        else:
            args=args+","+args_li[i]
    if neg:
        return("~"+pred+"("+args+")")
    else:
        return(pred+"("+args+")")

def unify(aClause, kb_length):
    ans = 0
    #print("UNIFICATION^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    #kb_length is the temp kb length u need to traverse through
    #go through each term in aclause
    for i in range(len(aClause)):
        aTerm = aClause[i]
        aPred = aTerm.predicate
        aNeg = aTerm.negation
        aArgs = aTerm.arguments
        a_sentence_num= aTerm.sentence_number
        no_of_terms_aClause= len(aClause)
        aVar=i+1 #token_number in clause

        if aNeg:
            neg_pred = aPred #negating the predicate, we get a positive predicate
            temp_pred ="~"+aPred #original predicate
            '''print("before negating", temp_pred)
            print("after negating", neg_pred)'''
        else:
            neg_pred ="~"+aPred #add negated symbol if the predicate is positive
            '''print("before negating", aPred)
            print("after negating", neg_pred)'''
        #if negated predicate is in the kb, then add that index to sentences_to_unify
        if neg_pred in predicate_dictionary.keys():
            #print(" is present")
            sentences_to_unify = predicate_dictionary[neg_pred]
        #when no negated predicate exists, no sentences to unify
        else:
            sentences_to_unify =[]

        #print("for predicate", aPred, "sentences to unify are", sentences_to_unify)
        # go through each sentence which can be unified:
        for k in range(len(sentences_to_unify)):
            b_sentence_num= sentences_to_unify[k]
            #gets the entire clause 
            bClause = temp_kb[sentences_to_unify[k]-1]
            unification_mapping={}
            variable_unification_mapping={}
            
            
            canBeUnified = True #saying aToken of aClause can be unified with entire bClause
            aTermIndexes=[] #term_indexes
            bTermIndexes=[]
            #todo
            newClauseList=[]
             #first_term_indexes
            
            
            for j in range(len(bClause)):
                
                
                bTerm = bClause[j]
                bPred = bTerm.predicate
                bNeg = bTerm.negation
                bArgs = bTerm.arguments
                no_of_terms_bClause= len(bClause)

                '''print("Trying to unify with term index"+str(j)+"in the second clause")
                print("OTHER predicate:",bPred)
                print("argument", bArgs)
                print("negation", bNeg)
                print("sentence_number_in_kb", b_sentence_num)'''

                bVar = j+1 #btoken number /term number  in the bClause
               
                #check if predicates are same and they are in opposition, if one is negated, other one should not be negated
                if(aPred== bPred and ((not aNeg and bNeg) or (aNeg and not bNeg))):
                    #print("Possibility of predicate resolution")
                    if(len(aArgs)== len(bArgs)):
                        length_of_arguments = len(aArgs)
                        for arg_index in range(length_of_arguments):
                            firstArg = aArgs[arg_index] 
                            secondArg = bArgs[arg_index]
                            if isVariable(firstArg) and isConstant(secondArg):
                                #print("first arg is variable and second arg is a constant")
                                unification_mapping[firstArg]=secondArg #replace variable of first sentence with constant
                                if i not in aTermIndexes:
                                    aTermIndexes.append(i)
                                    
                                if j not in bTermIndexes: # this is to hold which one of those terms in the bClause unifies
                                    bTermIndexes.append(j)
                                canBeUnified = True

                            elif isConstant(firstArg) and isVariable(secondArg):
                                #print("first arg is constant and second arg is a variable")
                                unification_mapping[secondArg]=firstArg#replace variable of first sentence with constant
                                if i not in aTermIndexes:
                                    aTermIndexes.append(i)
                                if j not in bTermIndexes: # this is to hold which one of those terms in the bClause unifies
                                    bTermIndexes.append(j)
                                canBeUnified = True

                            elif isVariable(firstArg) and isVariable(secondArg):
                                #print("Both args are variables, check if they are the same variables")

                                check = checkIfSame(firstArg, secondArg)
                                if not check: #remove if a problem
                                    unification_mapping[secondArg]=firstArg
                                #print("MAPPPPPPPIINNNNGGGG for variables", unification_mapping)
                                if i not in aTermIndexes:
                                    aTermIndexes.append(i)
                                if j not in bTermIndexes: # this is to hold which one of those terms in the bClause unifies
                                    bTermIndexes.append(j)
                                canBeUnified = True
                                #if both are different variables
                                #if not check:
                                #   variable_unification_mapping[first_arguments[arg_index]]=second_arguments[arg_index]
                                #   variable_unification_mapping[second_arguments[arg_index]]=first_arguments[arg_index]
                                #canBeUnified = True

                            elif isConstant(firstArg) and isConstant(secondArg):

                                check = checkIfSame(firstArg, secondArg)
                                #canbeunified means can it be unified with that particular predicate
                                if not check:
                                    #print("constant 1 and constant 2",firstArg,secondArg)
                                    #print("constants are different, so cant be unified. Break")
                                    canBeUnified = False
                                    #remove if fails
                                    unification_mapping={}
                                    break
                                else:
                                    if i not in aTermIndexes:
                                        aTermIndexes.append(i)
                                    if j not in bTermIndexes: # this is to hold which one of those terms in the bClause unifies
                                        bTermIndexes.append(j)
                                    canBeUnified = True
                            else:
                                canBeUnified = False
                                unification_mapping={}
                                break
                        '''print("A TERM INDEX", aTermIndexes)
                        print("B term index", bTermIndexes)

                        print("unification_mapping is",unification_mapping)
                        print("unification possible?", canBeUnified)
                        print("term_indexes in the first clause which can be unified", aTermIndexes)
                        print("term_indexes in the first clause which can be unified", bTermIndexes)'''

                        if(canBeUnified):
                            vars_can_be_unified = True
                            #print("SUBSTITUTION START")
                            flag=0
                            #todo
                            length = no_of_terms_bClause
                            term_indexes = bTermIndexes
                            #TODO
                            temp_length = len(temp_kb)

                            #if problem, change l to m
                            for m in range(length):
                                    
                                if m not in term_indexes:
                                    term = bClause[m]
                                    second_predicate = term.predicate
                                    second_arguments = term.arguments
                                    second_negation = term.negation
                                    second_sentence_number = term.sentence_number
                                    temp_args = []

                                    '''print("Substituting for")
                                    print(second_predicate)
                                    print(second_arguments)
                                    print("unification_mapping is",unification_mapping)'''
                                    for arg_index in range(len(second_arguments)):

                                                            
                                        if second_arguments[arg_index] in unification_mapping.keys():
                                            #print("SUBSTITUTE")
                                            #ARGUMENT IS SUBSTITUTED BY WHATEVER UNIFIED VALUE
                                            temp_args.append(unification_mapping[second_arguments[arg_index]])
                                        else:
                                            #ARGUMENT REMAINS AS BEFORE 
                                            temp_args.append(second_arguments[arg_index])

                                    set1=len(set(second_arguments))
                                    set2=len(set(temp_args))
                                    if set1!=set2:
                                        vars_can_be_unified= False
                                        break
                                        #break
                                        #todo
                                        #return 0


                                    newLiteral= Predicate(second_predicate, second_negation, temp_args, temp_length+1)
                                    newClauseList.append(newLiteral)
                                    '''print("****************ADDING New clause list*************")
                                    print(second_predicate)
                                    print(second_negation)
                                    print(temp_args)'''
                                        
                            #print("The final length of NEW CLAUSE LIST: ", len(newClauseList))
                            if(not vars_can_be_unified):
                                unification_mapping={}
                                bTermIndexes=[]
                                newClauseList=[]
                                continue

                            #add the remaining terms of the first clause
                            length= no_of_terms_aClause
                            term_indexes = aTermIndexes
                            '''print("length of first clause", length)
                            print("term indexes of first clause", term_indexes)'''

                            for m in range(length):
                                    
                                if m not in term_indexes:
                                    term = aClause[m]
                                    first_predicate= term.predicate
                                    first_arguments= term.arguments
                                    first_negation= term.negation
                                    first_sentence_number=term.sentence_number

                                    #print("first clause is ", first_predicate, first_arguments)
                                    temp_args=[]
                                    for arg_index in range(len(first_arguments)):
                                                            
                                        if first_arguments[arg_index] in unification_mapping.keys():
                                            #print("SUBSTITUTE")
                                            temp_args.append(unification_mapping[first_arguments[arg_index]])
                                        else:
                                            temp_args.append(first_arguments[arg_index])
                                    
                                    newLiteral= Predicate(first_predicate, first_negation, temp_args, temp_length+1)
                                    
                                    set1=len(set(first_arguments))
                                    set2=len(set(temp_args))
                                    if set1!=set2:
                                        vars_can_be_unified= False
                                        break
                                        #todo return false
                                        #return 0

                                    newClauseList.append(newLiteral)
                                    '''print("****************ADDING New clause list*************")
                                    print(first_predicate)
                                    print(first_negation)
                                    print(temp_args)'''
                            if(not vars_can_be_unified):
                                unification_mapping={}
                                bTermIndexes=[]
                                newClauseList=[]
                                continue
                            length_of_clauseList_now = len(newClauseList)
                            #UNCOMMENT
                            newClauseList= get_factored_clause(newClauseList)
                            if len(newClauseList)!=0:
                                check_kb=checkIfAlreadyInKB(newClauseList)
                                if not check_kb:
                                    temp_kb.append(newClauseList)

                                    #print("1.Length of kb is", len(temp_kb))
                                    #temp_length = temp_length+1
                                    if len(newClauseList)==1:
                                        check_if_negated=checkIfNegatedQueryInKB(newClauseList)
                                        if check_if_negated:
                                            ans = 1
                                            return ans

                                    #printKB()
                                    #print("length of kb is", len(temp_kb))
                                    #todo
                                unification_mapping={}
                                bTermIndexes=[]
                                newClauseList=[]
    return ans
                                
def resolve():
    kb_size_dif = -1
    count = 0
    len_kb_before=len(temp_kb)
    aClause = temp_kb[len_kb_before-1]
    
    ans=unify(aClause, len_kb_before)
    if ans:
        return True
    kb_size_dif = len(temp_kb)-len_kb_before

    while(kb_size_dif != 0):
        #same as var len_kb_before
        len_kb_before=len(temp_kb)#initially, temp_kb is same as kb
        #print("len_kb_before", len_kb_before)
        
        for i in range(kb_size_dif):
            if(count>=2500):
                return False
            count = count+1
            #print("CALLING RESOLVE FOR SENTENCE",len_kb_before-i-1)
            aClause = temp_kb[len_kb_before-i-1]
            ans=unify(aClause, len_kb_before)
            if ans:
                return True
            #printKB()

        kb_size_dif = len(temp_kb)-len_kb_before
        
        #print("COUNT ISSSSSSSSSSSSSSSSSSSSSS", count)
    return False

    
def main():
    global query_list
    query_list=[]

    global new_sentences_to_kb
    new_sentences_to_kb=[]

    global temp_kb
    temp_kb=[]

    processInputFile("input.txt")
    convertToCNF(sentences)
    #print("CNF CONVERTED STATEMENTS ARE:",cnf_statements)

    sentence_number_in_kb =createKB(cnf_statements)
    standardize(kb)
    ans = False
    ans_li=[]
    #print(predicate_dictionary)
    
    #printKB()
    #print("Adding queries to the KB:")
    
    #change to for i in range(num_queries):
    for i in range(num_queries):
        temp_kb = kb[:]
        alreadyTriedToResolve={}
        addQueryToKB(query_sentences[i], len(kb)+1)
        #printKB()
        sentence_number_in_kb = sentence_number_in_kb + 1
        #print("sentence number in kb",sentence_number_in_kb)
        ans = resolve()
        #print("answer is", ans)
        ans_li.append(ans)
        
    #printKB()
    print(ans_li)
    #print(predicate_dictionary)
    

main()
