"""
Generate a Private Key for an Image - uses hashlib,numpy and other basic operations.
It can be used to sign an image and needs optimization. 
Edit : A QR Code can be generated from the PrivateKey.
""" 

#!/usr/bin/python3
import cv2
import numpy
import pyexiv2
import pyqrcode
from hashlib import sha512
from operator import xor
from functools import reduce
from dataclasses import dataclass

@dataclass
class Data:
  SecuritClass = "Security/"
  ModifiedClass = "Modified/"
  SecurityTag = "Xmp.Security.Key"
  ModifiedTag = "Xmp.Modified.IsModified"
  InitialMod = "No"
  ModifiedAns = "Yes"
  QRMessage = "The following image has been identified with the following credentials : "

config = Data()

XOR = lambda x : [reduce(xor,j) for i in x for j in i]
CRITERIA = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,10,1.0)
FLAGS = cv2.KMEANS_RANDOM_CENTERS
FACTOR = 2  #Used only when downsampling the image (In ProcessImage method.)
class ImageEncoder:
  def __init__(self,imgpath)->None:
    """ Constructor """

    self._imgpath = imgpath
    self._img = cv2.imread(self._imgpath)
  
  def SetImageHash(self) -> str:
    """ Compute the Hash for the Image """

    prcsImage = self.ProcessImage()
    Hash = sha512(usedforsecurity = True)
    hashDigest = "".join(map(str,XOR(prcsImage)))
    Hash.update(bytes(hashDigest,encoding = "utf-8"))
    self._Hash = Hash.hexdigest() 

  def GetImageHash(self) -> str:
    """ Return the computed hash """

    return self._Hash  
  

  def GenerateQRCode(self,FileName:str,Scale:int = 8,ModuleColor:tuple = (0,0,0,255),BGColor:tuple = (255,255,255,255),QZ:int = 4 )->None:  
    """ Use QRCode as a digital watermark due to its robust namture and easy applyability. Call after the hash has been modified/generated"""
    md = pyexiv2.ImageMetadata(self._imgpath)
    md.read()

    modified = md._get_xmp_tag(config.ModifiedTag).value
    key = md._get_xmp_tag(config.SecurityTag).value
    qrcode = pyqrcode.create("{} \n IsModified : {} \n PrivateKey : {} \n ".format(config.QRMessage,modified,key))
    qrcode.png(FileName,Scale,ModuleColor,BGColor,QZ)
    print(qrcode.terminal(QZ))


  def RegisterNameSpace(self,metadata:pyexiv2.ImageMetadata) -> None:
    """ Register the required namespaces associated with the image(Xmp custom metadata) - the condition """

    if config.SecurityTag not in metadata.xmp_keys and config.ModifiedTag not in metadata.xmp_keys: #Make sure these are always together(SCE makes it difficult)
      pyexiv2.register_namespace(config.SecuritClass ,"Security")
      pyexiv2.register_namespace(config.ModifiedClass,"Modified")

      metadata[config.SecurityTag] = self._Hash
      metadata[config.ModifiedTag] = config.InitialMod

      metadata.write()

    else:
      _privateKey = metadata._get_xmp_tag(config.SecurityTag).value
      if _privateKey != self._Hash:
        metadata[config.ModifiedTag] = config.ModifiedAns
        metadata.write()

  def StampImage(self):
    """ Write the metadata in the image """

    metadata = pyexiv2.ImageMetadata(self._imgpath)
    metadata.read()    
    
    if "Xmp.Security.Key" not in metadata.xmp_keys:
      self.SetImageHash()
    
    else :
      self._Hash = None #To be decided on this later !
    
    self.RegisterNameSpace(metadata)
    self.GenerateQRCode("QR_for_Image.png")
    return self.GetImageHash()
  
  def ProcessImage(self,K=3):
    """Process the Image for faster computations. """
    
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
  
 
TestImagePath = "logo.png" #Add path of your image here.
PrivateKey = ImageEncoder(TestImagePath).StampImage()

# Display : print(PrivateKey)
