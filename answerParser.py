import re

'''
This function parses jeopardy clue solutions. 
Specifically, it parses off optional contents, 
article and check if the given solution contains 
alternatives. 

Args:
    s: solution parsed off from J-Archive (string)

Returns:
    All alternative solutions (list)
'''
# ideally, we also need a word to number function
# as well as roman numbers (Star Trek III)
def numberToWords(num):
      """
      :type num: int
      :rtype: str
      """
      if num == 0:
            return 'Zero'
      
      LESS_TAN_TWENTY = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
      TENS = ['', 'Ten', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
      THOUSANDS = ['', 'Thousand', 'Million', 'Billion']
      
      def helper(num):
            if num == 0:
                  return ''
            elif num < 20:
                  return LESS_TAN_TWENTY[num] + ' '
            elif num < 100:
                  return TENS[num/10] + ' ' + helper(num%10)
            else:
                  return LESS_TAN_TWENTY[num/100] + ' Hundred ' + helper(num%100)
      
      i, res = 0, ''
      while num > 0:
            if num % 1000 != 0:
                  res = helper(num%1000) + THOUSANDS[i] + ' ' + res
            num /= 1000
            i += 1
      return res.strip()

def main(s):
      # concert to lower case
      s = s.lower()
      a = []

      # "\"Anchors Aweigh\""
      # (1 of) Chicago White Sox & Boston Red Sox"

      # (James) Buchanan => Buchanan
      # Rocky (the Flying Squirrel)
      # MTBA (subway, metro) => MTAB, subway or metro

      if "/" in s:
            options = re.findall("(\w*)\/", s)
            last_option = re.findall("\/(\w+) ", s)
            options = options + last_option
            # print options
            remaining_strings = re.search("\/(\w+) (.*)$", s)
            ans = []
            if remaining_strings:
                  remaining_strings = remaining_strings.group(2)
                  ans = [re.sub('[^a-zA-Z0-9]', '', x + remaining_strings) for x in options]
            return ans

      if " of)" in s:
            # contents in ()
            s = re.sub(r'\([^()]*\)', '', s)

            a = re.split(r'\s*&\s*|\s*,\s*', s)
            a = filter(lambda x: x != 'or' and x != 'and' and x != '', a)

            # remove symbols and spaces
            a = [re.sub('a |an |the |&|[^a-zA-Z0-9]', '', temp) for temp in a]

            return a

      if len(re.findall(r'\(([^()]+)\)\s*$', s)) != 0:
            a = re.findall(r'\(([^()]+)\)\s*$', s)[0]
            # if there are multiple alternative answers, parse it off
            if ' accepted' in a:
                  a = re.sub(' accepted', '', a)

            if (' or ' in a):
                  a = re.split("\s*or\s*", a)
            elif len(re.findall(r'^or', a)) > 0:
                  a = re.sub('^or', '', a)
                  a = [a]
            else:
                  a = re.split("\s*,\s*", a)

            # remove all symbols 
            a = [re.sub('[^a-zA-Z0-9]', '', temp) for temp in a]
      elif " or " in s:
            # split on " or "
            a = re.split("\s*or\s*", s)

            # remove symbols and spaces
            a = [re.sub('[^a-zA-Z0-9]', '', temp) for temp in a]
            return a


      # parse off strings in ()
      s = re.sub(r'\([^()]*\)', '', s)

      # parse off beginning a, an, the
      s = re.sub(r'^the |^an |^a ', '', s)

      # remove all symbols 
      s = re.sub('[^a-zA-Z0-9]', '', s)

      if a:
            ans = [s] + a
      else:
            ans = [s]

      return ans
      
# s = "\"25 or 6 to 4\""
# s = "sold flowers (flower girl accepted)"
# s = "(2 of) Ionian, Doric, and Corinthian"
# s = "cartoonists (or animators)"
# s = "(2 of) the Montreal Expos, the Seattle Mariners, the California Angels, the Texas Rangers, the Toronto Blue Jays, & the Houston Astros"
# s = "under the chin (throat)"
# s = "Jack/Knave of Hearts"
# s = "Peru, Paraguay"
# print main(s)
