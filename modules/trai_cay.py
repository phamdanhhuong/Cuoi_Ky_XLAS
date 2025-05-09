# Ultralytics 🚀 AGPL-3.0 License - https://ultralytics.com/license

import io
from typing import Any

import cv2

from ultralytics import YOLO
from ultralytics.utils import LOGGER
from ultralytics.utils.checks import check_requirements
from ultralytics.utils.downloads import GITHUB_ASSETS_STEMS


class Inference:

    def __init__(self, **kwargs: Any):
        check_requirements("streamlit>=1.29.0")  # scope imports for faster ultralytics package load speeds
        import streamlit as st

        self.st = st  # Reference to the Streamlit module
        self.source = None  # Video source selection (webcam or video file)
        self.enable_trk = False  # Flag to toggle object tracking
        self.conf = 0.25  # Confidence threshold for detection
        self.iou = 0.45  # Intersection-over-Union (IoU) threshold for non-maximum suppression
        self.org_frame = None  # Container for the original frame display
        self.ann_frame = None  # Container for the annotated frame display
        self.vid_file_name = None  # Video file name or webcam index
        self.selected_ind = []  # List of selected class indices for detection
        self.model = None  # YOLO model instance

        self.temp_dict = {"model": None, **kwargs}
        self.model_path = None  # Model file path
        if self.temp_dict["model"] is not None:
            self.model_path = self.temp_dict["model"]

        LOGGER.info(f"Ultralytics Solutions: ✅ {self.temp_dict}")

    def web_ui(self):
        """Sets up the Streamlit web interface with custom HTML elements."""
        menu_style_cfg = """<style>MainMenu {visibility: hidden;}</style>"""  # Hide main menu style

        # Main title of streamlit application
        main_title_cfg = """<div><h1 style="color:#FF64DA; text-align:center; font-size:40px; margin-top:-50px;
        font-family: 'Archivo', sans-serif; margin-bottom:20px;">Nhận diện trái cây</h1></div>"""

        page_bg = """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Open+Sans&display=swap');

        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Open Sans', sans-serif;
            background-image: linear-gradient(
                rgba(0, 0, 0, 0.4), 
                rgba(0, 0, 0, 0.4)
            ), url("https://images.unsplash.com/photo-1465101162946-4377e57745c3?q=80&w=2078&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
            background-size: cover;
            background-position: center;
            color: white;
        }

        [data-testid="stHeader"] {
            background: rgba(255, 255, 255, 0);
        }

        h1, h2, h3 {
            color: #E0E0FF;
        }

        /* Style cho nút secondary */
        button[data-testid="stBaseButton-secondary"] {
            background: linear-gradient(to right, rgba(0, 0, 0, 0.7), rgba(50, 0, 100, 0.7));
            color: white;
            border: 1px solid white;
            padding: 10px 30px;
            border-radius: 10px;
            width: 260px;
            font-size: 16px;
            transition: all 0.3s ease;
        }

        button[data-testid="stBaseButton-secondary"]:hover {
            background: linear-gradient(to right, rgba(0, 0, 0, 0.9), rgba(50, 0, 100, 0.9));
            transform: scale(1.05);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            cursor: pointer;
        }

        </style>
        """

        # Set html page configuration and append custom HTML
        self.st.markdown(menu_style_cfg, unsafe_allow_html=True)
        self.st.markdown(main_title_cfg, unsafe_allow_html=True)
        self.st.markdown(page_bg, unsafe_allow_html=True)

    def sidebar(self):
        """Configure the Streamlit sidebar for model and inference settings."""
        self.st.sidebar.title("User Configuration")  # Add elements to vertical setting menu
        self.source = self.st.sidebar.selectbox(
            "Video",
            ("webcam", "video"),
        )  # Add source selection dropdown
        # self.enable_trk = self.st.sidebar.radio("Enable Tracking", ("Yes", "No"))  # Enable object tracking
        # self.conf = float(
        #     self.st.sidebar.slider("Confidence Threshold", 0.0, 1.0, self.conf, 0.01)
        # )  # Slider for confidence
        # self.iou = float(self.st.sidebar.slider("IoU Threshold", 0.0, 1.0, self.iou, 0.01))  # Slider for NMS threshold

        col1, col2 = self.st.columns(2)  # Create two columns for displaying frames
        self.org_frame = col1.empty()  # Container for original frame
        self.ann_frame = col2.empty()  # Container for annotated frame

    def source_upload(self):
        """Handle video file uploads through the Streamlit interface."""
        self.vid_file_name = ""
        if self.source == "video":
            vid_file = self.st.sidebar.file_uploader("Upload Video File", type=["mp4", "mov", "avi", "mkv"])
            if vid_file is not None:
                g = io.BytesIO(vid_file.read())  # BytesIO Object
                with open("ultralytics.mp4", "wb") as out:  # Open temporary file as bytes
                    out.write(g.read())  # Read bytes into file
                self.vid_file_name = "ultralytics.mp4"
        elif self.source == "webcam":
            self.vid_file_name = 0  # Use webcam index 0



    def configure(self):
        """Configure the model and load selected classes for inference."""
        # Add dropdown menu for model selection
        available_models = [x.replace("yolo", "YOLO") for x in GITHUB_ASSETS_STEMS if x.startswith("yolo11")]
        if self.model_path:  # If user provided the custom model, insert model without suffix as *.pt is added later
            available_models.insert(0, self.model_path.split(".pt")[0])
        selected_model = self.st.sidebar.selectbox("Model", available_models)

        with self.st.spinner("Model is downloading..."):
            self.model = YOLO(f"{selected_model.lower()}.pt")  # Load the YOLO model
            class_names = list(self.model.names.values())  # Convert dictionary to list of class names
        self.st.success("Model loaded successfully!")

        # Multiselect box with class names and get indices of selected classes
        selected_classes = self.st.sidebar.multiselect("Classes", class_names, default=class_names[:3])
        self.selected_ind = [class_names.index(option) for option in selected_classes]

        if not isinstance(self.selected_ind, list):  # Ensure selected_options is a list
            self.selected_ind = list(self.selected_ind)

    def inference(self):
        """Perform real-time object detection inference on video or webcam feed."""
        self.web_ui()  # Initialize the web interface
        self.sidebar()  # Create the sidebar
        self.source_upload()  # Upload the video source
        self.configure()  # Configure the app

        if self.st.sidebar.button("Start"):
            stop_button = self.st.button("Stop")  # Button to stop the inference
            cap = cv2.VideoCapture(self.vid_file_name)  # Capture the video
            if not cap.isOpened():
                self.st.error("Could not open webcam or video source.")
                return

            while cap.isOpened():
                success, frame = cap.read()
                if not success:
                    self.st.warning("Failed to read frame from webcam. Please verify the webcam is connected properly.")
                    break

                # Process frame with model
                if self.enable_trk == "Yes":
                    results = self.model.track(
                        frame, conf=self.conf, iou=self.iou, classes=self.selected_ind, persist=True
                    )
                else:
                    results = self.model(frame, conf=self.conf, iou=self.iou, classes=self.selected_ind)

                annotated_frame = results[0].plot()  # Add annotations on frame

                if stop_button:
                    cap.release()  # Release the capture
                    self.st.stop()  # Stop streamlit app

                self.org_frame.image(frame, channels="BGR")  # Display original frame
                self.ann_frame.image(annotated_frame, channels="BGR")  # Display processed frame

            cap.release()  # Release the capture
        cv2.destroyAllWindows()  # Destroy all OpenCV windows
    



# if __name__ == "__main__":
#     import sys  # Import the sys module for accessing command-line arguments

#     # Check if a model name is provided as a command-line argument
#     args = len(sys.argv)
#     model = sys.argv[1] if args > 1 else None  # Assign first argument as the model name if provided
#     model = "./model/best.pt"
#     # Create an instance of the Inference class and run inference
#     Inference(model=model).inference()
def show():
    import sys
    args = len(sys.argv)
    #model = sys.argv[1] if args > 1 else None
    model = "./model/best.pt"  # Hoặc đường dẫn model bạn muốn
    inf = Inference(model=model)
    inf.inference()