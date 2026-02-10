for i in range(5):
    print(i)


Name=input("Enter your name\n")
try:
    if Name == "":
        raise ValueError("Err") # ValueError is a string "Error"
except ValueError as e:
    print(e)


#astr = 'Hello Bob'
#a = int(astr)


# 3.1 Write a program to prompt the user for hours and rate per hour using input to compute gross pay. Pay the hourly rate for the hours up to 40 and 1.5 times the hourly rate for all hours worked above 40 hours. Use 45 hours and a rate of 10.50 per hour to test the program (the pay should be 498.75). You should use input to read a string and float() to convert the string to a number. Do not worry about error checking the user input - assume the user types numbers properly.
hrs = input("Enter Hours:")
h = float(hrs)
rate = input("Enter Rate per hour:")
r = float(rate)


if h <=40:
    print(h*r)
else:
    print(((h-40)*(1.5*r))+(40*r))

'''
3.3 Write a program to prompt for a score between 0.0 and 1.0. If the score is out of range, print an error. If the score is between 0.0 and 1.0, print a grade using the following table:
Score Grade
    >= 0.9 A
    >= 0.8 B
    >= 0.7 C
    >= 0.6 D
    < 0.6 F
If the user enters a value out of range, print a suitable error message and exit. For the test, enter a score of 0.85.
'''

score = input("Enter Score:")
s = float(score)
if s >= 0.9:
    print("A")
elif s >= 0.8:
    print("B")
elif s >= 0.7:
    print("C")
elif s >= 0.6:
    print("D")
elif s < 0.6:
    print("F")
else:
    print("Error: value is out of range")

'''
4.6 Write a program to prompt the user for hours and rate per hour using input to compute gross pay. 
Pay should be the normal rate for hours up to 40 and time-and-a-half for the hourly rate for all hours 
worked above 40 hours. Put the logic to do the computation of pay in a function called computepay() and 
use the function to do the computation. The function should return a value. Use 45 hours and a rate 
of 10.50 per hour to test the program (the pay should be 498.75). You should use input to read a 
string and float() to convert the string to a number. Do not worry about error checking the user 
input unless you want to - you can assume the user types numbers properly. Do not name your variable 
sum or use the sum() function.
'''

def computepay(h, r):
    if h > 40:
        return (40*r)+(h-40)*(r*1.5)
    else:
        return h*r

hrs = input("Enter Hours: \n")
rate = input("rate per hour: \n")
p = computepay(float(hrs), float(rate))
print("Pay", p)