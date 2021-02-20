"""VideoBarcode

Generates a "barcode" style visualization of an input video file

usage: main.py [-h] -n NFRAMES [-b [BLUR]] [-w WIDTH] source dest

positional arguments:
  source                Video filename
  dest                  Filename for the final image

optional arguments:
  -h, --help            show this help message and exit
  -n NFRAMES, --nFrames NFRAMES
                        Number of frames in final visualization
  -b [BLUR], --blur [BLUR]
                        Amount to blur if desired. Default 100
  -w WIDTH, --width WIDTH
                        Specify the width of each slice, Default 1px
"""

import argparse
import time
import cv2
import numpy


class BarcodeMaker:

    def makeBarcode(self, source, nFrames, blur, width, height):
        """
        Main function to generate the barcode image
        :param source: str, The source video file
        :param nFrames: int, The number of frames that should be rendered in the output image
        :param blur: int, Amount of motion blur
        :param width: int, Width of each slice
        :param height: int, Height of each slice
        :return: The output image
        """

        # Open the video file
        video = self.getVideoFile(source)
        # Calculate the interval and total # of frames in the video
        interval, totalFrames = self.getInterval(video, nFrames)
        # Get the height of the video if not specified by user
        if height is None:
            height = self.getHeight(video)

        completedFrames = 0
        nextFrame = interval / 2
        output = None

        # Mark the starting time for the elapsed time printout.
        startTime = time.time()
        print("Starting visualization of \"" + source + "\" ")

        while True:
            # The visualization is complete
            if completedFrames == nFrames:
                break

            # Set the cursor to the next frame to render
            video.set(cv2.CAP_PROP_POS_FRAMES, int(nextFrame))
            # Read the frame as an image
            valid, image = video.read()
            if not valid:
                raise IOError(
                    "Cannot read from video file at frame " + str(int(nextFrame)) + " out of " + str(totalFrames))

            # If this is the first time through, simply resize the frame
            if output is None:
                output = cv2.resize(image, (width, height))
            # Else concatenate the resized frame to the output
            else:
                output = cv2.hconcat([output, cv2.resize(image, (width, height))])

            completedFrames += 1  # Increment completed frames
            nextFrame += interval  # Set the next frame to render
            endChar = '\r' if completedFrames != nFrames else '\n'  # Print progress on same line unless completed
            timeElapsed = time.time() - startTime  # Calculate the elapsed time
            # format the time string
            timeString = "\tTime Elapsed: {}".format(time.strftime("%H:%M:%S", time.gmtime(timeElapsed)))
            # Print the progress bar
            print("Please wait ... " + str(completedFrames) + " out of " + str(nFrames) + " total frames " + timeString,
                  end=endChar)
        video.release()

        # If the user selected blur, apply it
        if blur != 0:
            print("Applying blur...")
            output = self.addBlur(output, blur)
        print("Done.")

        return output

    def getInterval(self, video, nFrames):
        """
        Calculate the interval between rendered frames and total frames
        :param video: The video
        :param nFrames: The number of frames to render
        :return: The interval, and total amount of frames
        """
        totalFrames = video.get(cv2.CAP_PROP_FRAME_COUNT)

        if nFrames < 1 or not isinstance(nFrames, int):
            raise ValueError("nFrames must be an integer greater than zero")
        elif nFrames > totalFrames:
            raise ValueError("nFrames is larger than the total available (" + totalFrames + ")")

        interval = totalFrames / nFrames

        return interval, totalFrames

    def getHeight(self, video):
        """
        Determine the height of the frames
        :param video: the video
        :return: the height
        """
        valid, image = video.read()

        if not valid:
            raise IOError("Cannot read from video file")

        return image.shape[0]

    def getVideoFile(self, source):
        """
        Open the video file as a OpenCV video
        :param source: the video filename
        :return: the video
        """
        video = cv2.VideoCapture(source)
        if not video.isOpened():
            raise FileNotFoundError("Video not found")

        return video

    def addBlur(self, image, amount):
        """
        Add a vertical motion blur to the image
        :param image: the image to apply blur to
        :param amount: the amount of blur
        :return: the blurred image
        """
        kernel = numpy.zeros((amount, amount))

        kernel[:, int((amount - 1) / 2)] = numpy.ones(amount)

        kernel /= amount

        return cv2.filter2D(image, -1, kernel)


def main():
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument("source", help="Video filename", type=str)
    parser.add_argument("dest", help="Filename for the final image", type=str)
    parser.add_argument("-n", "--nFrames", help="Number of frames in final visualization", type=int, required=True)
    parser.add_argument("-b", "--blur", help="Amount to blur if desired. Default 100", type=int, nargs='?', default=0,
                        const=100)
    parser.add_argument("-w", "--width", help="Specify the width of each slice, Default 1px", type=int, default=1)
    parser.add_argument("-h", "--height", help="Specify the height of each slice, Default calculates the height of "
                                               "the input frames", type=int, default=None)

    args = parser.parse_args()

    bm = BarcodeMaker()
    output = bm.makeBarcode(args.source, args.nFrames, args.blur, args.width, args.height)

    cv2.imwrite(args.dest, output)
    print("Visualization saved to {}".format(args.dest))


if __name__ == '__main__':
    main()
