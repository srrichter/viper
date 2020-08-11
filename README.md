# viper
Toolkit for VIPER benchmark

## Structure
The VIPER dataset is split into training, validation, and test set. 
Each subset is further divided into a number of video sequences.
Each video sequence was recorded in 1 of 5 environmental conditions (day, sunset, rain, night, snow).
The frame rate of each sequence is approximately 15 fps.

### Input images (img)
Each image was recorded in 1080p (1920x1080 pixels).
Due to the large number of frames, we provide the images in lossy JPG and lossless PNG format. 

### Camera calibration (camera)
We provide the camera calibration (intrinsic and extrinsic) as one CSV file for each video sequence.
Each line in the file encodes one frame with the first entry being the frame id and the remaining entries encoding the projection and the view matrices.
The 4x4 matrices are stored row-wise.
The poses for each sequence are relative to the first frame.
The coordinate system is right-handed with X pointing right, Y pointing up, and -Z pointing forward.
The camera used for capturing follows a pinhole model with the principal point at the image center.

### Semantic class segmentation labels (cls)
Labels are stored as indexed single channel 8-bit images with the mapping from
label IDs to semantic classes and colors provided in classes.csv

### Semantic instance segmentation labels (inst & instcs)
Semantic instance labels are encoded as 3-channel (RGB) 8-bit unsigned int images.
Here, the first channel (R) encodes the class ID, and the two remaining channels 
encode the instance ID (= 256 * G + B).

### 2D/3D Bounding boxes (bb)
We provide bounding boxes in 2D (on the image plane) and in 3D (in camera coordinate frame) for a subset of the semantic classes.
The annotations are stored as one CSV file per frame. 
Each row in one of the files corresponds to a single object instance.
The format for the columns is classID, instanceID, 2D bounding box (4 values), 3D bounding box in model coordinate frame (6 values), matrix to transform 3D bounding box into camera coordinate frame (16 values).

### Optical flow (flow)
The training and validation flow is stored as 16bit float Numpy npz format. For making a submission, we are expecting the Middlebury flo format, though. While the required conversion may be somewhat inconvenient, this approach enables a decent compression of the flow files as well as a standard format for evaluation. For making an optical flow submission, you currently need a Ubuntu system to run the encode_flow_submission app as part of the prepare_submission.py script.

