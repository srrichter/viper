## Evaluation
The test set we provide on our website is a superset of the test sets used for the benchmark evaluation of individual tasks. 
Hence, each task is evaluated on a subset of all the images in the test set.
You can find the list of images for each task on our download page.
More information for preparing your submission is given below in the task-specific sections.


### Semantic Class Segmentation
We expect a single zip file containing a predicted label map for each image in the test set.
The label maps should be single channel PNG files with a predicted class id for each pixel in the image.
The class ids and corresponding names can be found in the classes.csv.
The PNG files should follow the same naming scheme as the input images, thus predicting a segmentation for the 3rd image of sequence 002 should produce image

002_00003.png



### Semantic Instance Segmentation
For the instance segmentation evaluation, we expect a single zip file containg a set of PNG images and a file named 'instances.csv'.
Each PNG image is assumed to contain the (single channel) binary mask of a single instance of some class predicted for some input image.
Every nonzero pixel will be treated as belonging to the instance.
The name format for the PNG files should be the following (written as C printf format specification):

('%03d_%05d_%d_%d.png', sequence_id, frame_id, class_id, instance_id)


For example:
If your method predicts 3 cars (class_id=24 in classes.csv) in image 4 of 
sequence 002, it should produce images

002_00004_24_1.png
002_00004_24_2.png
002_00004_24_3.png


The 'instances.csv' should contain one line per instance 
(= one line per PNG image in the zip file of your submission).
Each line is expected to contain the following values 
(separated by commas as below):

sequence_id, image_id, class_id, instance_id, confidence

where confidence is a floating point value  between 0 and 1 expressing your method's
confidence in the prediction of this instance.
Revisiting the above example and assuming the confidences for the 3 predicted 
instances where 0.75, 0.5, and 0.6, your instances.csv should contain 3 lines:

2,4,24,1,0.75
2,4,24,2,0.5
2,4,24,3,0.6



### Optical Flow
For the evaluation we expect one .flo file per image pair.
The list of image pairs we evaluate can be found on the download page of our website.
The .flo format is the same as used in other benchmarks like Middlebury or Sintel. 
Since we are evaluating forward optical flow, the file name should match the first image of the pair, replacing the file extension with .flo ,
e.g., predicting flow for frames 3 and 4 of sequence 002 should produce a flow file

002_00003.flo


Correspondingly, the file list on our website contains per line the name of the first image, the second image, and the expected result file.
To compress the predicted flow files, please use the utility we provide (a link for downloading it will be presented during the submission process). 
It should be placed in the same folder as your prediction results.
Note that The tool expects all predicted .flo files in this folder and does not search any subfolders.
Running the tool from the command line should then produce a file

submission.bin


which you can submit to our servers for evaluating your predictions.
The submission.bin file will be ~400MB large.




### Visual Odometry
We expect a single zip file containing a .txt file with predicted poses for 
each sequence in the test set. The .txt should be named after the sequence, 
e.g., estimating poses for sequence 002 should leave you with a file named

002.txt


The files are expected to contain one line per predicted pose, where each line
contains the following (comma-separated) values:

timestamp, tx, ty, tz, qx, qy, qz, qw

where timestamp is the timestamp of each frame, t* is the position of the 
camera and q* is its rotation as quaternions. For compatibility, we expect the
same coordinate system as KITTI: 
x points right, y points down, z points forward.

Note that this is different from the bounding boxes we provide for 
3D object detection / scene layout estimation.

The list of sequences and timestamps can be taken from the list we provide 
on our website. Note that the sequences used in the odometry benchmark 
are different from the folder structure in the test set. 
The format in the provided sequence/timestamp lists is the following 
(again written in C printf format):

"%03d,%05d,%.4f\n", sequence_id_in_testset, frame_id, timestamp

Please also note that we use the timestamps to establish correspondences between
the poses your method predicted and the ground truth poses. Thus, non-matching 
timestamps will be ignored.

We handle missing frames the following way:
If frames are missing at the beginning or end of the sequence, we will simply
take the predicted pose for the first frame (or last frame, respectively) and 
duplicate it for every missing frame. If your method predicts poses only for 
some keyframes, poses for intermediate frames will be computed via linear 
interpolation (and slerp for the rotations).
