import argparse
import time
import cv2
import numpy


class BarcodeMaker:
    default_height = None
    default_width = 1

    def makeBarcode(self, source, nframes, blur, width=default_width, height=default_height):
        video = cv2.VideoCapture(source)
        if not video.isOpened():
            raise FileNotFoundError("Video not found")

        totalFrames = video.get(cv2.CAP_PROP_FRAME_COUNT)
        if not isinstance(nframes, int) or nframes < 1:
            raise ValueError("Number of frames must be a positive integer")
        elif nframes > totalFrames:
            raise ValueError("Number of frames is larger than total available (" + str(totalFrames) + ")")
        interval = totalFrames / nframes
        success, image = video.read()
        if not success:
            raise IOError("Cannot read from video file")
        if height is None:
            height = image.shape[0]

        completedFrames = 0
        nextFrame = interval / 2
        output = None

        startTime = time.time()
        print("Starting visualization of \"" + source + "\" ")

        while True:
            if completedFrames == nframes:
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
            endChar = '\r' if completedFrames != nframes else '\n'
            timeElapsed = time.time() - startTime
            timeString = "\tTime Elapsed: {}".format(time.strftime("%H:%M:%S", time.gmtime(timeElapsed)))
            print("Please wait ... " + str(completedFrames) + " out of " + str(nframes) + timeString, end=endChar)
        video.release()

        if blur != 0:
            print("Applying blur...")
            output = self.addBlur(output, blur)
        print("Done.")

        return output

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
    parser.add_argument("-n", "--nframes", help="Number of frames in final visualization", type=int, required=True)
    parser.add_argument("-b", "--blur", help="Amount to blur if desired. Default 100", type=int, nargs='?', default=0,
                        const=100)
    parser.add_argument("-w", "--width", help="Specify the width to use, Default 1px", type=int, default=1)

    args = parser.parse_args()

    bm = BarcodeMaker()
    output = bm.makeBarcode(args.source, args.nframes, args.blur, args.width)

    cv2.imwrite(args.dest, output)
    print("Visualization saved to {}".format(args.dest))


if __name__ == '__main__':
    main()
