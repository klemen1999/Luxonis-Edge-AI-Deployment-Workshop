#!/usr/bin/env python3

import argparse
from datetime import timedelta
from pathlib import Path
import cv2
import depthai as dai
import numpy as np
import time
from depthai_nodes.node import HostParsingNeuralNetwork, YOLOExtendedParser

DISPLAY_SIZE = (1280, 1280)
THRESHOLD_STEP = 0.05

parser = argparse.ArgumentParser(description="Run a YOLO detection network from a local NN archive.")
parser.add_argument(
    "-m",
    "--model",
    type=Path,
    required=True,
    help="Path to the local NN archive (.tar.xz).",
)
args = parser.parse_args()

if not args.model.is_file():
    parser.error(f"NN archive not found: {args.model}")

nnArchive = dai.NNArchive(str(args.model))

# Create pipeline
with dai.Pipeline() as pipeline:
    cameraNode = pipeline.create(dai.node.Camera).build()
    # The NN runs on the device, the YOLO parser runs on the host so its thresholds can change at runtime.
    detectionNetwork = pipeline.create(HostParsingNeuralNetwork).build(cameraNode, nnArchive)
    detectionParser = detectionNetwork.getParser(YOLOExtendedParser)

    # Both outputs are square and use CROP, so the normalized detections map directly onto the display frame.
    displayOutput = cameraNode.requestOutput(DISPLAY_SIZE)

    # Pair each display frame with the detections from the same capture.
    sync = pipeline.create(dai.node.Sync)
    sync.setRunOnHost(True)
    sync.setSyncThreshold(timedelta(milliseconds=10))
    displayOutput.link(sync.inputs["rgb"])
    detectionNetwork.out.link(sync.inputs["detections"])
    qSync = sync.out.createOutputQueue()

    pipeline.start()
    print("Controls: w/s confidence +/- 0.05, e/d IoU +/- 0.05, q quit.")
    print(f"Confidence: {detectionParser.conf_threshold:.2f}, IoU: {detectionParser.iou_threshold:.2f}")

    startTime = time.monotonic()
    counter = 0
    color2 = (255, 255, 255)

    # nn data, being the bounding box locations, are in <0..1> range - they need to be normalized with frame width/height
    def frameNorm(frame, bbox):
        normVals = np.full(len(bbox), frame.shape[0])
        normVals[::2] = frame.shape[1]
        return (np.clip(np.array(bbox), 0, 1) * normVals).astype(int)

    def displayFrame(name, frame, detections):
        color = (255, 0, 0)
        textColor = (255, 255, 255)
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 0.8
        thickness = 2
        padding = 4
        for detection in detections:
            bbox = frameNorm(
                frame,
                (detection.xmin, detection.ymin, detection.xmax, detection.ymax),
            )
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            # Label and confidence on a filled tag above the box, or inside it at the top frame edge.
            text = f"{detection.labelName} {detection.confidence * 100:.0f}%"
            (textW, textH), baseline = cv2.getTextSize(text, font, fontScale, thickness)
            tagH = textH + baseline + 2 * padding
            tagTop = bbox[1] - tagH if bbox[1] >= tagH else bbox[1]
            cv2.rectangle(frame, (bbox[0], tagTop), (bbox[0] + textW + 2 * padding, tagTop + tagH), color, cv2.FILLED)
            cv2.putText(
                frame,
                text,
                (bbox[0] + padding, tagTop + padding + textH),
                font,
                fontScale,
                textColor,
                thickness,
                cv2.LINE_AA,
            )
        # Show the frame
        cv2.imshow(name, frame)

    def stepThreshold(value, delta):
        return round(max(0.0, min(1.0, value + delta)), 2)

    while pipeline.isRunning():
        msgGroup: dai.MessageGroup = qSync.get()
        inRgb: dai.ImgFrame = msgGroup["rgb"]
        inDet: dai.ImgDetections = msgGroup["detections"]
        counter += 1

        frame = inRgb.getCvFrame()
        cv2.putText(
            frame,
            "NN fps: {:.2f}".format(counter / (time.monotonic() - startTime)),
            (2, frame.shape[0] - 4),
            cv2.FONT_HERSHEY_TRIPLEX,
            0.4,
            color2,
        )
        displayFrame("rgb", frame, inDet.detections)

        key = cv2.waitKey(1)
        if key in (ord("w"), ord("s")):
            delta = THRESHOLD_STEP if key == ord("w") else -THRESHOLD_STEP
            detectionParser.setConfidenceThreshold(stepThreshold(detectionParser.conf_threshold, delta))
            print(f"Confidence: {detectionParser.conf_threshold:.2f}, IoU: {detectionParser.iou_threshold:.2f}")
        elif key in (ord("e"), ord("d")):
            delta = THRESHOLD_STEP if key == ord("e") else -THRESHOLD_STEP
            detectionParser.setIouThreshold(stepThreshold(detectionParser.iou_threshold, delta))
            print(f"Confidence: {detectionParser.conf_threshold:.2f}, IoU: {detectionParser.iou_threshold:.2f}")
        elif key == ord("q"):
            pipeline.stop()
            break
