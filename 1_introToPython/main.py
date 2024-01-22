import math

angle_deg = 65
# angle_rad = math.radians(angle_deg)
angle_rad = math.pi * angle_deg / 180

sin = math.sin(angle_rad)
cos = math.cos(angle_rad)

print("sin({}) = {}".format(angle_deg, sin))
print("cos({}) = {}".format(angle_deg, cos))

'''
Create two tuples: p1 and p2, set their values to (2,3), (5,7) respectively.
Write a function that takes two 2D points p1 and p2  , and computes the Euclidean distance between them using the formula:
distance = math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
Finally, print the distance between p1 and p2.
'''

p1 = (2, 3)
p2 = (5, 7)

def distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

print("distance between {} and {} is {}".format(p1, p2, distance(p1, p2)))