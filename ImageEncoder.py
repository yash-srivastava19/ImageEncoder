"""
Generate a Private Key for an Image - uses hashlib,numpy and other basic operations.
It can be used to sign an image and needs optimization. 
""" 

#!/usr/bin/python3
import cv2
import numpy
import pyexiv2
from hashlib import sha512
from operator import xor
from functools import reduce

XOR = lambda x : [reduce(xor,j) for i in x for j in i]
CRITERIA = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,10,1.0)
FLAGS = cv2.KMEANS_RANDOM_CENTERS
FACTOR = 2  #Used only when downsampling the image (In ProcessImage method.)
class ImageEncoder:
  def __init__(self,img)->None:
    self._img = img
  
  def ImageHash(self) -> str:
    prcsImage = self.ProcessImage(5)
    Hash = sha512(usedforsecurity = True)
    hashDigest = "".join(map(str,XOR(prcsImage)))
    Hash.update(bytes(hashDigest,encoding = "utf-8"))
    digest = Hash.hexdigest()
    self.StampInImage(digest)
    return digest
  
  def ProcessImage(self,K=3):
    # If the color features of the image needs to be enhanced(for security reason) - you can convert the image to HSV(uncomment to use this feature).
    """
    self._img = cv2.cvtColor(self._img,cv2.COLOR_BGR2HSV)
    """
    
    #Additionally, if the time needs to be reduced, consider downsampling the image(uncomment to use this feature).
    
    """ 
    rows,cols,channels = map(int,self._img.shape)
    self._img = cv2.pyrDown(self._img,dstsize=(cols//FACTOR,rows//FACTOR))  
    """
    
    cImage = self._img.reshape((-1,3)).astype(numpy.float32)
    ret,label,center = cv2.kmeans(cImage,K,None,CRITERIA,10,FLAGS)
    center = numpy.uint8(center)
    resImage = (center[label.flatten()]).reshape((self._img.shape))
    return resImage
  
  def StampInImage(self,_Hash)-> None:
    """ Stamps the hash in the image metadata. """

    metadata = pyexiv2.ImageMetadata(self._imgpath)
    metadata.read()
    
    """Register a new namespace to maintain clarity"""
    
    pyexiv2.unregister_namespaces()
    pyexiv2.register_namespace("Security/","Security")
    metadata['Xmp.Security.Key'] = _Hash

    metadata.write()
 
TestImage = cv2.imread("add/path/to/image/here") #Add path of your image here.
PrivateKey = ImageEncoder(TestImage).ImageHash()

# Display : print(PrivateKey)
