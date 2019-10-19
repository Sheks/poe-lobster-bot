
def make_black_and_white(image):
    thresh = 177
    fn = lambda x : 255 if x > thresh else 0
    img = image.convert('L').point(fn, mode='1')
    return img


def make_dithered(image):
    r = image.convert('1')
    return r