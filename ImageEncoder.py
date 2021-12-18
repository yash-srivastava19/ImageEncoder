"""
Generate a Private Key for an Image - uses hashlib,numpy and other basic operations.
It can be used to sign an image and needs optimization.
Edit : A QR Code can be generated from the PrivateKey.
"""

# !/usr/bin/python3
import cv2
import time
import numpy
import pyexiv2
from hashlib import sha512
from operator import xor
from functools import reduce
from dataclasses import dataclass


@dataclass
class Data:
    SecurityClass = "Security/"
    ModifiedClass = "Modified/"
    SecurityTag = "Xmp.Security.Key"
    ModifiedTag = "Xmp.Modified.IsModified"
    InitialMod = "No"
    ModifiedAns = "Yes"


config = Data()

XOR = lambda x: [reduce(xor, j) for i in x for j in i]
CRITERIA = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
FLAGS = cv2.KMEANS_RANDOM_CENTERS
FACTOR = 2


class ImageEncoder:
    def __init__(self, img_path: str) -> None:
        """ Constructor """
        self._Hash = None
        self._imgpath = img_path
        self._img = cv2.imread(self._imgpath)
        self._metadata = pyexiv2.ImageMetadata(self._imgpath)
        self._metadata.read()
        if config.SecurityTag in self._metadata.xmp_keys:
            self.set_image_hash(self._metadata._get_xmp_tag(config.SecurityTag).value)
            self.check_authenticity()
        else:
            self.register_namespace()

    def set_image_hash(self, value) -> None:
        """ Set the hash for the Image """
        self._Hash = value

    def calculate_hash(self) -> str:
        """ Calculate the hash associated with the image """
        Hash = sha512(usedforsecurity=True)
        prng = numpy.random.MT19937(self.feature_transform())
        a = numpy.atleast_3d(prng.random_raw((self._img.shape[1])))
        hashDigest = "".join(map(str, XOR(a)))
        Hash.update(bytes(hashDigest, encoding="utf-8"))
        return Hash.hexdigest()

    def get_image_hash(self) -> str:
        """ Return the computed hash """
        return self._Hash

    def feature_transform(self) -> numpy.array:
        """ Get the feature array for a given image"""
        sift = cv2.SIFT_create()
        _, des = sift.detectAndCompute(self._img, None)
        return des.astype(numpy.int)

    def register_namespace(self) -> None:
        """ Register the required namespaces associated with the image(Xmp custom metadata) - the condition """
        self._metadata.read()
        pyexiv2.register_namespace(config.SecurityClass, "Security")
        pyexiv2.register_namespace(config.ModifiedClass, "Modified")

        self.set_image_hash(self.calculate_hash())
        self._metadata[config.SecurityTag] = self.get_image_hash()
        self._metadata[config.ModifiedTag] = config.InitialMod

        self._metadata.write()

    def check_authenticity(self):
        """ Check whether the tags are same as we found  """
        _privateKey = self.calculate_hash()
        if _privateKey != self.get_image_hash():
            self._metadata.read()
            self._metadata[config.ModifiedTag] = config.ModifiedAns
            self._metadata.write()

        return self.get_image_hash()

    def process_image(self, K=5):
        """ Process the Image """
        # self._img = cv2.cvtColor(self._img, cv2.COLOR_BGR2HSV)
        # rows, cols, channels = map(int, self._img.shape)
        # self._img = cv2.pyrDown(self._img, dstsize=(cols//FACTOR, rows//FACTOR)) 
        cImage = self._img.reshape((-1, 3)).astype(numpy.float32)
        ret, label, center = cv2.kmeans(cImage, K, None, CRITERIA, 10, FLAGS)
        center = numpy.uint8(center)
        resImage = (center[label.flatten()]).reshape(self._img.shape)
        return resImage


TestImagePath = "add/path/to/image/here"  # Add path of your image here.
ie = ImageEncoder(TestImagePath)
