import cv2
from pyzbar import pyzbar
import qrcode


def create_qr(path, text):
    """
    Create a qr code of the text in the path provided with the text as the filename.
    :param path: the path (folder) provided.
    :param text: the text to be encoded as a qr code.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )

    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(path + text + ".png")


def read_barcodes(frame):
    """
    Read the barcodes shown on the given frame and returns the frame with the decoded code/s.
    :param frame: frame of a video.
    :return: the frame with the qr code/s marked and labeled with the decoded text/s and the decoded string.
    """
    barcodes = pyzbar.decode(frame)
    barcode_info = None

    # Reading all bar/qr codes in the frame. Returning info of the last qr code
    for barcode in barcodes:
        x, y, w, h = barcode.rect

        barcode_info = barcode.data.decode('utf-8')
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, barcode_info, (x + 6, y - 6), font, 2.0, (255, 255, 255), 1)

    return frame, barcode_info


def camera_scan():
    """
    Enabling the camera to scan bar/qr codes with opencv.
    :return: the decoded text (of the first qr/bar code if there's more than one codes).
    """
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    while True:
        ret, frame = camera.read()
        frame, qrcode_info = read_barcodes(frame)
        cv2.imshow('Barcode/QR code reader', frame)

        if qrcode_info is not None:
            break

        if cv2.waitKey(1) & 0xFF == 27:
            break

        if cv2.getWindowProperty('Barcode/QR code reader', cv2.WND_PROP_VISIBLE) < 1:
            break

    camera.release()
    cv2.destroyAllWindows()
    return qrcode_info
