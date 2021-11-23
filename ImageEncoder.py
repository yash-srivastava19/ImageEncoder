"""
Generate a Private Key for an Image - uses hashlib,numpy and other basic operations.
It can be used to sign an image and needs optimization. 
""" 

#!/usr/bin/python3
import cv2
import numpy
from hashlib import sha512
from operator import xor
from functools import reduce

XOR = lambda x : [reduce(xor,j) for i in x for j in i]
CRITERIA = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,10,1.0)
FLAGS = cv2.KMEANS_RANDOM_CENTERS

class ImageEncoder:
  def __init__(self,img)->None:
    self._img = img
  
  def ImageHash(self) -> str:
    prcsImage = self.ProcessImage(5)
    Hash = sha512(usedforsecurity = True)
    hashDigest = "".join(map(str,XOR(prcsImage)))
    Hash.update(bytes(hashDigest,encoding = "utf-8"))
    return Hash.hexdigest()
  
  def ProcessImage(self,K=3):
    cImage = self._img.reshape((-1,3)).astype(numpy.float32)
    ret,label,center = cv2.kmeans(cImage,K,None,CRITERIA,10,FLAGS)
    center = numpy.uint8(center)
    resImage = (center[label.flatten()]).reshape((self._img.shape))
    return resImage
 
TestImage = cv2.imread("add/path/to/image/here") #Add path of your image here.
PrivateKey = ImageEncoder(TestImage).ImageHash()

# Display : print(PrivateKey)
