import re
import pyzbar.pyzbar as pyzbar
from PIL import Image

def decode_barcode(img_file):
    img = Image.open(img_file.file)
    decoded_objs = pyzbar.decode(img)

    barcodes = []
    for obj in decoded_objs:
        if obj.type != 'QRCODE':
            barcode = re.findall("\d+", str(obj.data))
            if barcode:
                barcodes.append(barcode[0])
    return barcodes