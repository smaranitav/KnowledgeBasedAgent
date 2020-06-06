# KnowledgeBasedAgent
Developed a KB-agent(Knowledge based agent) which works by using first-order logic resolution to infer if a certain statement is entailed by the knowledge base. Input data will be encoded as first order logic clausesin the knowledge base. The program takes a query of new drug list and provide a logical conclusion whether to issue a warning.The program takes a query and the output is a logical conclusion based on the statements in the knowledge base. Worked on this project during the course of CSCI-561 Artificial Intelligence at USC. 

# Overview
This project was developed as a beta version of a self-service automated system to alert customers about potential drug interactions for both prescription and over-the-counter drugs. Patient history and drug compatibility data will be encoded as first order logic clauses
in the knowledge base. The program takes a query of new drug list and provide a logical conclusion whether to issue a warning.

# NOTE
This program works for any knowledge base as long as the sentences in knowledge base comply with the requirements as shown below

# Format for input.txt
<N = NUMBER OF QUERIES>
<QUERY 1>
…
<QUERY N>
<K = NUMBER OF GIVEN SENTENCES IN THE KNOWLEDGE BASE>
<SENTENCE 1>
…
<SENTENCE K>
  
The first line contains an integer N specifying the number of queries. The following N lines contain
one query per line. The line after the last query contains an integer K specifying the number of
sentences in the knowledge base. The remaining K lines contain the sentences in the knowledge
base, one sentence per line.
# Query format: 
Each query will be a single literal of the form Predicate(Constant_Arguments) or
~Predicate(Constant_Arguments) and will not contain any variables. Each predicate will have
between 1 and 25 constant arguments. Two or more arguments will be separated by commas.

# KB format: 
Each sentence in the knowledge base is written in one of the following forms:
1) An implication of the form p1 ∧ p2 ∧ ... ∧ pm ⇒ q, where its premise is a conjunction of
literals and its conclusion is a single literal. Remember that a literal is an atomic sentence
or a negated atomic sentence.
2) A single literal: q or ~q
Note:
1. & denotes the conjunction operator.
2. | denotes the disjunction operator. It will not appear in the queries nor in the KB given as
input. But you will likely need it to create your proofs.
3. => denotes the implication operator.
4. ~ denotes the negation operator.


