#!/usr/bin/env python3

import argparse
from pathlib import Path
import depthai as dai
from depthai_nodes.node import HostParsingNeuralNetwork, YOLOExtendedParser

DISPLAY_SIZE = (1280, 1280)
THRESHOLD_STEP = 0.05


class ThresholdOverlay(dai.node.ThreadedHostNode):
    """Publish threshold values and controls alongside each detection message."""

    def __init__(self):
        super().__init__()
        self.inputDet = self.createInput()
        self.output = self.createOutput()

    def build(self, detections, detection_parser):
        detections.link(self.inputDet)
        self.detection_parser = detection_parser
        return self

    def run(self):
        while self.mainLoop():
            detections = self.inputDet.get()
            overlay = dai.ImgAnnotations()
            overlay.setTimestamp(detections.getTimestamp())
            overlay.setSequenceNum(detections.getSequenceNum())
            overlay.setTransformation(detections.getTransformation())
            annotation = dai.ImgAnnotation()
            lines = [
                f"Confidence: {self.detection_parser.conf_threshold:.2f}  [w + / s -]",
                f"IoU: {self.detection_parser.iou_threshold:.2f}  [e + / d -]",
                f"Step: {THRESHOLD_STEP:.2f}  |  [q] Quit",
            ]
            for index, line in enumerate(lines):
                text = dai.TextAnnotation()
                text.position = dai.Point2f(0.02, 0.04 + index * 0.04)
                text.text = line
                text.fontSize = 24
                text.textColor = dai.Color(1.0, 1.0, 1.0, 1.0)
                text.backgroundColor = dai.Color(0.0, 0.0, 0.0, 0.75)
                annotation.texts.append(text)
            overlay.annotations.append(annotation)
            self.output.send(overlay)


parser = argparse.ArgumentParser(
    description="Run a YOLO detection network from a local NN archive."
)
parser.add_argument(
    "-m",
    "--model",
    type=Path,
    required=True,
    help="Path to the local NN archive (.tar.xz).",
)
parser.add_argument(
    "-d",
    "--device",
    metavar="IP",
    help="Device IP address. Omit to select an available device automatically.",
)
parser.add_argument(
    "--fps",
    type=int,
    default=30,
    help="Camera preview and encoder frame rate (positive integer, default: 30).",
)
args = parser.parse_args()

if args.fps <= 0:
    parser.error("--fps must be greater than zero")

if not args.model.is_file():
    parser.error(f"NN archive not found: {args.model}")

nnArchive = dai.NNArchive(str(args.model))

visualizer = dai.RemoteConnection(httpPort=8082)

# Create pipeline
device = dai.Device(dai.DeviceInfo(args.device)) if args.device else dai.Device()
with device, dai.Pipeline(device) as pipeline:
    cameraNode = pipeline.create(dai.node.Camera).build()
    # The NN runs on the device, the YOLO parser runs on the host so its thresholds can change at runtime.
    detectionNetwork = pipeline.create(HostParsingNeuralNetwork).build(
        cameraNode, nnArchive
    )
    detectionParser = detectionNetwork.getParser(YOLOExtendedParser)

    # Both outputs are square and use CROP, so the normalized detections map directly onto the display frame.
    displayOutput = cameraNode.requestOutput(
        DISPLAY_SIZE, type=dai.ImgFrame.Type.NV12, fps=args.fps
    )
    # Encode on the device to reduce preview bandwidth to the host and browser.
    encoder = pipeline.create(dai.node.VideoEncoder)
    encoder.setDefaultProfilePreset(
        args.fps, dai.VideoEncoderProperties.Profile.H264_MAIN
    )
    displayOutput.link(encoder.input)

    thresholdOverlay = pipeline.create(ThresholdOverlay).build(
        detectionNetwork.out, detectionParser
    )

    visualizer.addTopic("Camera", encoder.out)
    visualizer.addTopic("Detections", detectionNetwork.out)
    visualizer.addTopic("Controls", thresholdOverlay.output)

    pipeline.start()
    visualizer.registerPipeline(pipeline)

    print("Pipeline started")

    def stepThreshold(value, delta):
        return round(max(0.0, min(1.0, value + delta)), 2)

    while pipeline.isRunning():
        key = visualizer.waitKey(1)
        if key in (ord("w"), ord("s")):
            delta = THRESHOLD_STEP if key == ord("w") else -THRESHOLD_STEP
            detectionParser.setConfidenceThreshold(
                stepThreshold(detectionParser.conf_threshold, delta)
            )
        elif key in (ord("e"), ord("d")):
            delta = THRESHOLD_STEP if key == ord("e") else -THRESHOLD_STEP
            detectionParser.setIouThreshold(
                stepThreshold(detectionParser.iou_threshold, delta)
            )
        elif key == ord("q"):
            pipeline.stop()
            break
