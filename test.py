import base64
from io import BytesIO
from PIL import Image
import os

root = os.path.split(os.path.abspath(__file__))[0]
STATIC_IMAGE_PATH = os.path.join(root, 'web_solution', 'static', 'images')
RESULT_IMAGE = os.path.join(STATIC_IMAGE_PATH, 'result_images')

img = Image.open(os.path.join(RESULT_IMAGE, '1688099498.8336632-image1.png'))
buffered = BytesIO()
img.save(buffered, format='PNG')
im_base64 = base64.b64encode(buffered.getvalue())
with open("demofile2.txt","wb") as f:
    # f.write(base64.decodestring(im_base64))
    f.write(im_base64)
  
print('base64: ', im_base64)