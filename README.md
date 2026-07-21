# VirtualBrush ✋🎨

Real-time, touchless drawing application that tracks hand landmarks through a
webcam and lets you paint in the air with your index finger — no stylus, no
touchscreen, no gloves.

![status](https://img.shields.io/badge/status-active-brightgreen)
![python](https://img.shields.io/badge/python-3.9%2B-blue)
![opencv](https://img.shields.io/badge/OpenCV-4.9-orange)
![mediapipe](https://img.shields.io/badge/MediaPipe-0.10-yellowgreen)

<!-- Add a demo GIF here once recorded -->
<!-- ![demo](docs/demo.gif) -->

## Overview

VirtualBrush uses [MediaPipe Hands](https://developers.google.com/mediapipe) to
extract 21 3D hand landmarks per frame at real-time speed on CPU, then
applies lightweight geometric rules to classify finger state and gesture
intent. A persistent canvas is alpha-blended onto the live camera feed so
strokes remain visible and stable across frames.

**Why this project matters:** it demonstrates an end-to-end real-time CV
pipeline — capture → inference → state management → rendering — using the
same architectural pattern found in production AR/gesture-control systems,
without requiring custom model training or a GPU.

## Features

- Real-time hand tracking (single hand, extendable to two)
- Gesture-based mode switching:
  - ☝️ Index finger only → draw
  - ✌️ Index + middle → hover / select (no drawing)
  - ✊ Fist → idle
- On-screen color palette + eraser, selected by hovering
- Exponential smoothing on stroke points to suppress landmark jitter
- Live FPS counter for performance visibility
- Save canvas to PNG, clear canvas, all via keyboard shortcuts

## Architecture