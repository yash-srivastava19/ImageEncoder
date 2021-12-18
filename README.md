# ImageEncoder
A simple private key generator for a particular image. It uses basic operations on image and stamps the private key in the image metadata.

## v.1.0.1
ImageEncoder went through a major revision in v.1.0.1 to prevent a major flaw in logic. In the previous version, changing just a single pixel craeted an avalanche effect - which might not ideal in many cases. To counter this flaw, we implemented a simple feature extractor using SIFT(Scale Invariant Feature Transform) to detect keypoints in the image. This is then used as a seed for Mersenne Twister Pseudo Random Number Generator(MT19937). From this PRNG, some selected elements are chosen of a particular size. These random number are then shuffled and XORed within one channel, as done previously. From this, the story is similar to the previous version. 

<p> The second version also saw removal of QRCode, which was added just as a unique feature - However it can be integrated in future versions(and this version too). It is separate from the Encoder, and it is better to keep it that way.</p>

---
### Additional Resources
[Mersenne Twister](https://en.wikipedia.org/wiki/Mersenne_Twister)
[SIFT](https://en.wikipedia.org/wiki/Scale-invariant_feature_transform)
