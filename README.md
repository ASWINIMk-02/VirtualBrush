# VirtualBrush – Air Drawing using OpenCV & MediaPipe

## Project Overview

(Short description)

## Features

- Real-time hand tracking
- Air drawing
- Multiple colors
- Eraser
- Save drawing
- Clear canvas
- Lightweight and fast

## Architecture

![VirtualBrush Architecture](docs/architecture.png)

## Technologies Used

- Python 3.12
- OpenCV
- MediaPipe
- NumPy

## Project Structure

```text
VirtualBrush/
│── docs/
│   ├── architecture.png
│   ├── hand_detection.png
│   ├── drawing.png
│   ├── color_change.png
│   └── final_output.png
│
│── air_draw.py
│── README.md
│── requirements.txt
│── LICENSE
└── .gitignore
```

## Installation

Clone the repository:

```bash
git clone https://github.com/ASWINIMK-02/VirtualBrush.git
```

Move into the project folder:

```bash
cd VirtualBrush
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python air_draw.py
```

## Usage

1. Start the application.
2. Allow webcam access.
3. Raise only your **Index Finger** to draw.
4. Raise **Index + Middle Finger** to select a color.
5. Hover over **ERASE** to erase drawings.
6. Press:
   - `C` → Clear Canvas
   - `S` → Save Drawing
   - `Q` → Quit Application

## Screenshots

### Hand Detection

![Hand Detection](docs/hand_detection.png)

### Drawing

![Drawing](docs/drawing.png)

### Color Selection

![Color Selection](docs/color_change.png)

### Final Output

![Final Output](docs/final_output.png)

## Future Improvements

- Add Clear button on screen
- Add Save button on screen
- Add Brush Size Selection
- Add Undo / Redo
- Support Multiple Hands
- Add Gesture Customization
- Improve UI Design

## Author

**Aswini M**

B.Tech (Hons.) Computer Science Engineering (AI & ML)

Periyar Maniammai Institute of Science and Technology

GitHub: https://github.com/ASWINIMK-02

## License

This project is licensed under the MIT License.
