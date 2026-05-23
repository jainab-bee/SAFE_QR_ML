import numpy as np
import cv2

try:
    import zxingcpp
    HAS_ZXING = True
except:
    HAS_ZXING = False

try:
    from pyzbar.pyzbar import decode as pyzbar_decode
    HAS_PYZBAR = True
except:
    HAS_PYZBAR = False


def read_qr_code(pil_image):
    rgb = pil_image.convert("RGB")
    img_array = np.array(rgb)
    bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    if HAS_ZXING:
        try:
            found = zxingcpp.read_barcodes(img_array)
            if found:
                return found[0].text.strip()
        except:
            pass

        for scale in [2, 3]:
            try:
                big = cv2.resize(gray, (gray.shape[1] * scale, gray.shape[0] * scale), interpolation=cv2.INTER_CUBIC)
                big_rgb = cv2.cvtColor(big, cv2.COLOR_GRAY2RGB)
                found = zxingcpp.read_barcodes(big_rgb)
                if found:
                    return found[0].text.strip()
            except:
                pass

        try:
            _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            bw_rgb = cv2.cvtColor(bw, cv2.COLOR_GRAY2RGB)
            found = zxingcpp.read_barcodes(bw_rgb)
            if found:
                return found[0].text.strip()
        except:
            pass

    if HAS_PYZBAR:
        try:
            decoded = pyzbar_decode(pil_image)
            if decoded:
                return decoded[0].data.decode("utf-8").strip()
        except:
            pass

    detector = cv2.QRCodeDetector()

    for img in [bgr, gray]:
        try:
            data, _, _ = detector.detectAndDecode(img)
            if data and data.strip():
                return data.strip()
        except:
            pass

    for scale in [2, 3, 4]:
        try:
            big = cv2.resize(gray, (gray.shape[1] * scale, gray.shape[0] * scale), interpolation=cv2.INTER_CUBIC)
            data, _, _ = detector.detectAndDecode(big)
            if data and data.strip():
                return data.strip()
        except:
            pass

    return ""
