# tool for acheiving temporal consistency by using inpainting on a lower quadrant for each frame


import shutil
import modules.scripts as scripts
import gradio as gr
import os
from PIL import Image
import numpy as np
import torch

from modules import images
import modules.shared as shared
import cv2
from moviepy.editor import *

# mostly copied from temporal kit
def copy_video(source_path, destination_path):
    """
    Copy a video file from source_path to destination_path.

    :param source_path: str, path to the source video file
    :param destination_path: str, path to the destination video file
    :return: None
    """
    try:
        shutil.copy(source_path, destination_path)
        print(f"Video copied successfully from {source_path} to {destination_path}")
    except IOError as e:
        print(f"Unable to copy video. Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# mostly copied from temporal kit
def makeTemplate(srcVideo, folder):

    print("making template! ", folder)

    main_video_path = os.path.join(folder,"main_video.mp4")
    copy_video(srcVideo,main_video_path)

   

    """
    split each video frame into a numpy array
    """
    # Open the video file for reading
    cap = cv2.VideoCapture(srcVideo)

    # Initialize an empty list to store the frames
    frames = []

    # Loop through each frame in the video
    while True:
        print('reading video frame')

        # Read the next frame from the video
        ret, frame = cap.read()

        # If the frame was not read successfully, we have reached the end of the video
        if not ret:
            break

        correctFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert the frame to a numpy array and append it to the frames list
        frame_np = np.array(correctFrame)
        frames.append(frame_np)

    # Release the video file handle and print the number of frames read
    cap.release()


    if(len(frames) <4):
        print("didn't find enough frames to make a template")
        return



    # Define the target height for resizing the images
    target_height = 768/2

    # Define the input list of numpy images
    images = frames
#
    # Resize all images to have the target height while maintaining their aspect ratio
    resized_images = []
    for image in images:
        h, w = image.shape[:2]
        ratio = target_height / h
        new_size = (int(w * ratio), int(h * ratio))
        resized_image = Image.fromarray(image).resize(new_size, Image.ANTIALIAS)
        resized_images.append(np.array(resized_image))

    # Create a new composite image with a 2x2 grid layout
    composite_image = Image.new('RGB', (resized_images[0].shape[1] * 2, resized_images[0].shape[0] * 2))

    # Paste the first 4 images into the composite image
    composite_image.paste(Image.fromarray(resized_images[0]), (0, 0))
    composite_image.paste(Image.fromarray(resized_images[1]), (resized_images[0].shape[1], 0))
    composite_image.paste(Image.fromarray(resized_images[2]), (0, resized_images[0].shape[0]))
    composite_image.paste(Image.fromarray(resized_images[3]), (resized_images[0].shape[1], resized_images[0].shape[0]))

    return composite_image

def prepInpainting(srcVideo, folder, srcTemplate):


    inputImageFolder = os.path.join(folder, "inputs")
    if not os.path.exists(inputImageFolder):
        os.makedirs(inputImageFolder)
    else:
        shutil.rmtree(inputImageFolder)
        os.makedirs(inputImageFolder)

    maskImageFolder = os.path.join(folder, "masks")
    if not os.path.exists(maskImageFolder):
        os.makedirs(maskImageFolder)
    else:
        shutil.rmtree(maskImageFolder)
        os.makedirs(maskImageFolder)

    outputImageFolder = os.path.join(folder, "outputs")
    if not os.path.exists(outputImageFolder):
        os.makedirs(outputImageFolder)
    else:
        shutil.rmtree(outputImageFolder)
        os.makedirs(outputImageFolder)


    """
    split each video frame into a numpy array
    """
    # Open the video file for reading
    cap = cv2.VideoCapture(srcVideo)

    # Initialize an empty list to store the frames
    frames = []

    # Loop through each frame in the video
    while True:
        print('reading video frame')

        # Read the next frame from the video
        ret, frame = cap.read()

        # If the frame was not read successfully, we have reached the end of the video
        if not ret:
            break

        correctFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert the frame to a numpy array and append it to the frames list
        frame_np = np.array(correctFrame)
        frames.append(frame_np)

    # Release the video file handle and print the number of frames read
    cap.release()


    target_height = 768/2
    """
    create inputs
    """
    for i in range(len(frames)):
        image = frames[i]
        h, w = image.shape[:2]

        ratio = target_height / h
        newW = int(w * ratio)
        newH = int(h * ratio)
        new_size = (newW, newH)
        print('new size', type(new_size))
        resized_image = cv2.resize(image, dsize=new_size, interpolation=cv2.INTER_CUBIC)

        composite_image = Image.new('RGB', (2*newW, 2*newH))
        composite_image.paste(Image.fromarray(srcTemplate), (0, 0)) 
        composite_image.paste(Image.fromarray(resized_image), (newW, newH))
        filepath = os.path.join(inputImageFolder, str(i) + ".png")
        print('working on file path', filepath, newW, newH)
        composite_image.save(filepath, format='PNG')



        mask_image = Image.new('RGB', (2*newW, 2*newH), color='black')

        # Create a white box in the bottom right corner
        box_width = newW
        box_height = newH
        box_pos = (2*newW - box_width, 2*newH - box_height)
        box = Image.new('RGB', (box_width, box_height), color='white')
        mask_image.paste(box, box_pos)

        maskfilepath = os.path.join(maskImageFolder, str(i) + ".png")
        mask_image.save(maskfilepath, format='PNG')


# mostly copied from temporal kit
def pil_images_to_video(pil_images, output_file, fps=24):
    """
    Saves an array of PIL images to a video file using MoviePy.

    Args:
        pil_images (list): A list of PIL images.
        output_file (str): The output file path for the video.
        fps (int, optional): The desired frames per second. Defaults to 24.

    Returns:
        the filepath of the video file
    """
    # Convert PIL images to NumPy arrays
    np_images = [np.array(img) for img in pil_images]

    # Create an ImageSequenceClip instance with the array of NumPy images and the specified fps
    clip = ImageSequenceClip(np_images, fps=fps)

    # Write the video file to the specified output location
    clip.write_videofile(output_file,fps,codec='libx264')

    return output_file

def recombineVideo(folder):
    path = os.path.join(folder,"outputs")

    outputFile = os.path.join(folder, "output.mp4")
    if(os.path.exists(outputFile)):
        os.remove(outputFile)


    # List all image files in the folder
    image_files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.png') and not '-' in f]

    # Load each image, extract the bottom right quarter, and store in a list
    images = []

    # Define a function to extract the number from the file name
    def extract_number(filename):
        return int(''.join(filter(str.isdigit, filename)))

    # Sort the image files by the number at the end of the file name
    image_files.sort(key=extract_number)

    for filename in image_files:
        # Load the image using OpenCV
        image = cv2.imread(filename)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Extract the bottom right quarter of the image
        height, width, _ = image.shape
        quarter_height = height // 2
        quarter_width = width // 2
        bottom_right = image[quarter_height:height, quarter_width:width]

        # Convert the image to a PIL Image object
        pil_image = Image.fromarray(bottom_right)

        # Append the image to the list
        images.append(pil_image)

    # Create a new image with the same size as the first image
    first_image = images[0]
    width, height = first_image.size
    #output_image = Image.new('RGB', (width//2, height//2), color='black')

    # Save the output image as a video using OpenCV

    #fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')


    pil_images_to_video(images, outputFile, 30)

    return outputFile
    


class Script(scripts.Script):

    im2gr = 5

    def title(self):
        return "Temporal Hop"


    def show(self, is_img2img):
        if is_img2img:
            return True
        return False
    



    def ui(self, is_img2img):

        gr.Text("Step 0: Create a folder for inputs / outputs / processing")
        folderInput = gr.Textbox(label="Input folder")
        
        gr.Text("Step 1: Input your source video")
        srcVideo = gr.Video(elem_id='srcVideo', source="upload", interactive=True, visible=True, type="filepath")
        
        gr.Text("Step 2: Press Make template")
        makeTemplateButton = gr.Button("Make Template", label="Make Template")
        originalTemplate = gr.Image(elem_id='originalTemplate', source="canvas", interactive=False, visible=True)
        makeTemplateButton.click(fn=makeTemplate, inputs=[srcVideo, folderInput], outputs=[originalTemplate])

        gr.Text("Step 3: Put the edited template here")
        srcTemplate = gr.Image(elem_id='srcTemplate', source="upload", interactive=True, visible=True)
        
        gr.Text("Step 4: Prepare inpainting batch using your edited template")
        prepInpaintingButton = gr.Button("Prepare inpainting batch", label="Prepare inpainting batch")
        prepInpaintingButton.click(fn=prepInpainting, inputs=[srcVideo, folderInput, srcTemplate])

        gr.Text("Step 5: Do batch img2img. Copy the folder /input, /output, and /masks. Make sure to use the same settings you used when editing the template. Controlnet should also work")
        
        gr.Text("Step 6: After doing the batch, click here to recombine the video")
        recombineVideoButton = gr.Button("Recombine Video", label="Recombine Video")


        gr.Text("Step 7: Enjoy your video! (check outputs folder)")
        destVideo = gr.Video(elem_id='destVideo', interactive=False, visible=True)
        recombineVideoButton.click(fn=recombineVideo, inputs=[folderInput], outputs=[destVideo])


        return [folderInput, srcVideo, makeTemplateButton, srcTemplate, prepInpaintingButton, recombineVideoButton, destVideo]