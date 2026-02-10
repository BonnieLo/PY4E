
greet = 'Hello Bob'
#to upper
zap = greet.upper()
print(zap)

zap = greet.join(['Hi ', ' there'])
print(zap)

zap = greet.split()
print(zap)  

zap = greet.startswith('Hello')
print(zap)

data = 'From stephen.marquard@uct.ac.za Sat Jan  5 09:14:16 2008'
pos = data.find('.')
print(data[pos:pos+3])

'''
6.5 Write code using find() and string slicing (see section 6.10) to extract the number 
at the end of the line below. Convert the extracted value to a floating point number and print it out.
'''

text = "X-DSPAM-Confidence:    0.8475"
pos = text.find('0')
print(float(text[pos:])) 
