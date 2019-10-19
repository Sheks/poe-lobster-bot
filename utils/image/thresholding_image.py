from PIL import Image


# Method to process the red band

def pixelProcRed(intensity):
    return 0


# Method to process the blue band

def pixelProcBlue(intensity):
    return intensity


# Method to process the green band

def pixelProcGreen(intensity):
    return intensity


# Create an image object
def threshold_image(imageObject):

    # Split the red, green and blue bands from the Image
    multiBands = imageObject.split()

    # Apply point operations that does thresholding on each color band
    redBand = multiBands[0].point(pixelProcRed)
    greenBand = multiBands[1].point(pixelProcGreen)
    blueBand = multiBands[2].point(pixelProcBlue)

    # Display the individual band after thresholding
    redBand.show()
    greenBand.show()
    blueBand.show()

    # Create a new image from the thresholded red, green and blue brands
    newImage = Image.merge("RGB", (redBand, greenBand, blueBand))

    return newImage