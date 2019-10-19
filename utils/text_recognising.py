import pytesseract

def get_text_from_image(image):
    return pytesseract.image_to_string(image, lang='rus')