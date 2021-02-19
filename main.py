import argparse
import time
import cv2
import numpy


class BarcodeMaker:
    default_height = None

    def makeBarcode(self, source, nFrames, blur, width, height=default_height):

        video = self.getVideoFile(source)
        interval, totalFrames = self.getInterval(video, nFrames)
        height = self.getHeight(video, height)

        completedFrames = 0
        nextFrame = interval / 2
        output = None

        startTime = time.time()
        print("Starting visualization of \"" + source + "\" ")

        while True:
            if completedFrames == nFrames:
                break

            video.set(cv2.CAP_PROP_POS_FRAMES, int(nextFrame))
            success, image = video.read()
            if not success:
                raise IOError(
                    "Cannot read from video file at frame " + str(int(nextFrame)) + " out of " + str(totalFrames))

            if output is None:
                output = cv2.resize(image, (width, height))
            else:
                output = cv2.hconcat([output, cv2.resize(image, (width, height))])

            completedFrames += 1
            nextFrame += interval
            endChar = '\r' if completedFrames != nFrames else '\n'
            timeElapsed = time.time() - startTime
            timeString = "\tTime Elapsed: {}".format(time.strftime("%H:%M:%S", time.gmtime(timeElapsed)))
            print("Please wait ... " + str(completedFrames) + " out of " + str(nFrames) + timeString, end=endChar)
        video.release()

        if blur != 0:
            print("Applying blur...")
            output = self.addBlur(output, blur)
        print("Done.")

        return output

    def getInterval(self, video, nFrames):
        totalFrames = video.get(cv2.CAP_PROP_FRAME_COUNT)

        if nFrames < 1 or not isinstance(nFrames, int):
            raise ValueError("nFrames must be an integer greater than zero")
        elif nFrames > totalFrames:
            raise ValueError("nFrames is larger than the total available (" + totalFrames + ")")

        interval = totalFrames / nFrames

        return interval, totalFrames

    def getHeight(self, video, height):
        valid, image = video.read()

        if not valid:
            raise IOError("Cannot read from video file")
        if height is None:
            height = image.shape[0]

        return height

    def getVideoFile(self, source):
        video = cv2.VideoCapture(source)
        if not video.isOpened():
            raise FileNotFoundError("Video not found")

        return video

    def addBlur(self, image, amount):
        kernel_h = numpy.zeros((amount, amount))

        kernel_h[:, int((amount - 1) / 2)] = numpy.ones(amount)

        kernel_h /= amount

        imageBlurred = cv2.filter2D(image, -1, kernel_h)

        return imageBlurred


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("source", help="Video filename", type=str)
    parser.add_argument("dest", help="Filename for the final image", type=str)
    parser.add_argument("-n", "--nFrames", help="Number of frames in final visualization", type=int, required=True)
    parser.add_argument("-b", "--blur", help="Amount to blur if desired. Default 100", type=int, nargs='?', default=0,
                        const=100)
    parser.add_argument("-w", "--width", help="Specify the width to use, Default 1px", type=int, default=1)

    args = parser.parse_args()

    bm = BarcodeMaker()
    output = bm.makeBarcode(args.source, args.nFrames, args.blur, args.width)

    cv2.imwrite(args.dest, output)
    print("Visualization saved to {}".format(args.dest))


if __name__ == '__main__':
    main()
