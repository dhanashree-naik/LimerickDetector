#!/usr/bin/env python
import argparse
import sys
import codecs
if sys.version_info[0] == 2:
  from itertools import izip
else:
  izip = zip
from collections import defaultdict as dd
import re
import os.path
import gzip
import tempfile
import shutil
import atexit

# Use word_tokenize to split raw text into words
from string import punctuation

import nltk
from nltk.tokenize import word_tokenize
#from nltk.tokenize import RegexpTokenizer

scriptdir = os.path.dirname(os.path.abspath(__file__))

reader = codecs.getreader('utf8')
writer = codecs.getwriter('utf8')

def prepfile(fh, code):
  if type(fh) is str:
    fh = open(fh, code)
  ret = gzip.open(fh.name, code if code.endswith("t") else code+"t") if fh.name.endswith(".gz") else fh
  if sys.version_info[0] == 2:
    if code.startswith('r'):
      ret = reader(fh)
    elif code.startswith('w'):
      ret = writer(fh)
    else:
      sys.stderr.write("I didn't understand code "+code+"\n")
      sys.exit(1)
  return ret

def addonoffarg(parser, arg, dest=None, default=True, help="TODO"):
  ''' add the switches --arg and --no-arg that set parser.arg to true/false, respectively'''
  group = parser.add_mutually_exclusive_group()
  dest = arg if dest is None else dest
  group.add_argument('--%s' % arg, dest=dest, action='store_true', default=default, help=help)
  group.add_argument('--no-%s' % arg, dest=dest, action='store_false', default=default, help="See --%s" % arg)



class LimerickDetector:

    def __init__(self):
        """
        Initializes the object to have a pronunciation dictionary available
        """
        self._pronunciations = nltk.corpus.cmudict.dict()
    
    def guess_syllables(self, word):
        word=word.lower()
        count = 0
        vow_dict = ['a','e','i','o','u']
        vowel = ['y']
        if word[0] in vow_dict:
            count+=1
        for i in range (1 , len(word)):
            if word[i] in vow_dict and not word[i-1] in vow_dict :
                count+=1
            if word[i] in vowel and not word[i-1] in vow_dict :
                count+=1
                
        if word.endswith('e'):
            if not word[-2] in vow_dict:
                count-=1
            if word.endswith('ue'):
                return self.guess_syllables(word[:-2])
            if word.endswith('le'):
                count+=1
        if word.endswith('y'):
            if word.endswith('fully') and word != 'fully' :
                return self.guess_syllables(word[:-2])
            
        if word.endswith('ed'):
            count-=1 
            
        if word.endswith('es'):
            if not word[:-2].endswith('s') and not word[:-2].endswith('ss') and not word[:-2].endswith('ch') and not word[:-2].endswith('x') and not word[:-2].endswith('z') and not word[:-2].endswith('sh') and not word[:-2].endswith('c'):
                return self.guess_syllables(word[:-1])
            
            
                
        if  'ia' in word:
            count+=1
        if  word.startswith('natural'):
            count-=1
              
        
        if word.endswith('ism') :
            count+=1 
            if word.endswith('uism') :  
                count+=1    
                                                 
        if count ==0 :
            count = 1   
        return count        
    
    def apostrophe_tokenize(self,line):
        tokenizer = nltk.tokenize.RegexpTokenizer( r'[\w\']+') 
        
        return tokenizer.tokenize(line)
        
    def num_syllables(self, word):
        """
        Returns the number of syllables in a word.  If there's more than one
        pronunciation, take the shorter one.  If there is no entry in the
        dictionary, return 1.
        """
        word=word.lower()
        num =[]
        if word in self._pronunciations:
            
            for pronoun in self._pronunciations[word]:
                count = 0
                for i in pronoun:
                     if i[-1].isdigit():
                        count=count+1
                num.append(count)
            return min(num)
        
        return 1

    def rhymes(self, a, b):
        vow_dict = set('aeiouAEIOU')
        """
        Returns True if two words (represented as lower-case strings) rhyme,
        False otherwise.
        """
        a=a.lower()
        b=b.lower()      
        a_pronunciation = []
        b_pronunciation = []
        sound=[]
        
        if a in self._pronunciations:
            first_list = self._pronunciations[a]
            for pronoun in first_list:                
                string_a = ""
                for letter_group in pronoun:
                    if  not vow_dict.isdisjoint(letter_group):
                        sound=pronoun[pronoun.index(letter_group):]    
                        break  
          
                for i in sound:
                    string_a=string_a+str(i)
                a_pronunciation.append(string_a)
                    
        if b in self._pronunciations:
            second_list = self._pronunciations[b]
            for pronoun in second_list:
                string_b = ""
                for letter_group in pronoun:
                    if  not vow_dict.isdisjoint(letter_group):
                        sound=pronoun[pronoun.index(letter_group):]
                        break

                for i in sound:
                    string_b=string_b+str(i)
                b_pronunciation.append(string_b)
                    
        if len(b)<=len(a):
            for wordb in b_pronunciation:
                for worda in a_pronunciation:
                    if worda.endswith(wordb):
                        return True
        else :
            for wordb in b_pronunciation:
                for worda in a_pronunciation:
                    if wordb.endswith(worda):
                        return True               

       

        return False

    def is_limerick(self, text):
   
        """
        Takes text where lines are separated by newline characters.  Returns
        True if the text is a limerick, False otherwise.

        A limerick is defined as a poem with the form AABBA, where the A lines
        rhyme with each other, the B lines rhyme with each other, and the A lines do not
        rhyme with the B lines.


        Additionally, the following syllable constraints should be observed:
          * No two A lines should differ in their number of syllables by more than two.
          * The B lines should differ in their number of syllables by no more than two.
          * Each of the B lines should have fewer syllables than each of the A lines.
          * No line should have fewer than 4 syllables

        (English professors may disagree with this definition, but that's what
        we're using here.)
        

        """
        
        text = text.lower().strip()
        
        A=[]
        A_line=[]
        B_line=[]
        B=[]
        A_syllable=[]
        B_syllable=[]
        count = 0
        flag1=0
        flag2=0
        flag3=0
        flag4=0
        flag5=0
        flag6=0
        

        #tokenizer = RegexpTokenizer( r'[\w\']+') 
        text2 = text.splitlines()
        if (len(text2)>5):
        
            for i in text2:
                if i == "" :
                    del text2[text2.index(i)]
                
        
        if (len(text2)==5):
            #split the text in lines and store the last words
            for line in text2 :
                line=line.strip()
                line = re.sub(r"[^\w\s']",'',line)
                line_token=word_tokenize(line)
                
                if count==0 or count==1 or count ==4 :
                    A.append(line_token[-1])
                    A_line.append(line_token)
                else :
                    B.append(line_token[-1])
                    B_line.append(line_token)
                count= count +1

            for line in A_line:
                a_count=0
                for word in line:
                    a_count = a_count + self.num_syllables(word)
                A_syllable.append(a_count)

            for line in B_line:
                b_count=0
                for word in line:
                    b_count = b_count + self.num_syllables(word)
                B_syllable.append(b_count)       
                    
           
            if (self.rhymes(A[0],A[1]) and self.rhymes(A[2],A[1]) and self.rhymes(A[0],A[2]) and self.rhymes(B[0],B[1])): 
                flag1=1 
            
            for b in B:
               for a in A:
                    if not self.rhymes(a,b):
                        flag6=1
                        break
            
            if abs(A_syllable[0]-A_syllable[1]) <= 2 and (A_syllable[1]-A_syllable[2]) <=2 and abs(A_syllable[0]-A_syllable[2]) <=2 and abs(B_syllable[0]-B_syllable[1]<= 2):
                flag2 =1
                
            for b in B_syllable:
                if b>=4:
                    flag3=1
                for a in A_syllable:
                    if a >= 4:
                        flag4=1
                    if b < a:
                        flag5=1
            
            if flag1 and flag6 and flag2 and flag3 and flag4 and flag5 :
                return True
           
                    
            
            
       
        return False



def main():
  parser = argparse.ArgumentParser(description="limerick detector. Given a file containing a poem, indicate whether that poem is a limerick or not",
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  addonoffarg(parser, 'debug', help="debug mode", default=False)
  parser.add_argument("--infile", "-i", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="input file")
  parser.add_argument("--outfile", "-o", nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="output file")




  try:
    args = parser.parse_args()
  except IOError as msg:
    parser.error(str(msg))

  infile = prepfile(args.infile, 'r')
  outfile = prepfile(args.outfile, 'w')

  ld = LimerickDetector()
  lines = ''.join(infile.readlines())
  outfile.write("{}\n-----------\n{}\n".format(lines.strip(), ld.is_limerick(lines)))
  
  
  

if __name__ == '__main__':
  main()
