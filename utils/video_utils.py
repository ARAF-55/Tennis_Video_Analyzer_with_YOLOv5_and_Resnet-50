import os
import cv2

def read_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    return frames

    """
    def read_images_from_folder(folder_path):
    frames = []
    
    # Get a list of all image file names in the folder
    image_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.jpg')])
    
    for image_file in image_files:
        # Create the full path to the image file
        image_path = os.path.join(folder_path, image_file)
        
        # Read the image using OpenCV
        frame = cv2.imread(image_path)
        
        # Append the image (frame) to the frames list
        frames.append(frame)
    
    return frames
    """


def save_video(output_video_frames, output_video_path):
    fourcc = cv2.VideoWriter.fourcc(*'MJPG')
    out = cv2.VideoWriter(output_video_path, fourcc, 24,
                          (output_video_frames[0].shape[1], output_video_frames[0].shape[0]))
    for frame in output_video_frames:
        out.write(frame)
    out.release()
