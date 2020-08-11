import os
import csv
import argparse
import pathlib
import zipfile
import shutil

"""'Prepare submission files for the VIPER benchmark ("https://playing-for-benchmarks.org").'"""


def _get_flow_test_frames():
	frames = []
	with open('flow_frames.txt') as fin:
		for line in fin:
			frames.append(line.strip())
			pass
		pass
	return sorted(frames)


def _get_test_frames():
	return _get_flow_test_frames() + ['005_00025', '022_02193', '023_00991', '042_00485', '048_00500', '053_00935']


def _get_test_frame_paths(path, ext):
	return [path / (f + ext) for f in _get_test_frames()]


def _get_instance_clsids():
	return [13,16,17,19,20,23,24,25,26,27]


def encode(outpath, app_path, frame_path):
	""" Encodes frames to a binary submission file.
		Needed for optical flow and monodepth."""

	app_dst_path    = frame_path / app_path.name
	submission_path = frame_path / 'submission.bin'

	shutil.copy(app_path, app_dst_path)
	os.system('cd %s; ./%s' % (frame_path, app_path.name))
	
	if submission_path.exists():
		shutil.move(submission_path, outpath)
		return True
	return False


def zip(outpath, files):
	with zipfile.ZipFile(outpath, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
		for file in files:
			archive.write(file)
			pass
		pass
	pass

	
def _check_frames(path, frame_paths):

	print('Checking for frames ...', end='',  flush=True)
	missing = [p for p in frame_paths if not p.exists()]
	
	if not missing:
		print('Ok')
		return True
	else:
		ready_for_submission = False
		print('Missing')
		print('\tMissing frames (%d in total):' % (len(missing)))
		for f in missing:
			print('\t\t%s' % f)
			pass
		return False
	return False


def check_cls_submission(path):
	"""Checks if all files required for the submission exist and are in the right format."""

	ready_for_submission = True
	ready_for_submission = ready_for_submission and _check_frames(path, _get_test_frame_paths(path, '.png'))
	return ready_for_submission


def finalize_cls_submission(path, outpath):
	"""Creates a submittable file for semantic class segmentations."""

	if check_cls_submission(path):
		print('Preparing submission ...', end='', flush=True)
		
		files = _get_test_frame_paths(path, '.png')
		
		submission_path = outpath if outpath is not None else (path / 'cls_submission.zip')
		zip(submission_path, files)
		
		print('Ok')
		print('Submission file is "%s". Please upload it at "https://playing-for-benchmarks.org"' % submission_path)
		pass
	else:
		print('Files are not ready for a submission yet.')
		pass
	return


def _parse_instance_supp(path):
	""" Parses the user-provided instances.csv file for an instance segmentation submission. 
		The file should list all predicted instances and correspond to images depicting individual instance masks.
	"""

	fieldnames = ['sequence', 'frame_id' , 'class_id', 'instance_id', 'score']

	frames = {}
	with open(path / 'instances.csv') as csvfile:
		sample = csvfile.read(1024)
		csvfile.seek(0)
		sniffer = csv.Sniffer()
		tab = csv.DictReader(csvfile, \
			fieldnames=(None if sniffer.has_header(sample) else fieldnames), \
			dialect=sniffer.sniff(sample))
		for row in tab:
			frame_id   = '%03d_%05d' % (int(row['sequence']), int(row['frame_id']))
			frame_path = path / ('%s_%d_%d.png' % (frame_id, int(row['class_id']), int(row['instance_id'])))
			if frame_id not in frames:
				frames[frame_id] = [frame_path]
			else:
				frames[frame_id].append(frame_path)
				pass
			pass
		pass
	return frames


def _print_inst_format():
	print('\tThe file should be a CSV with the following columns: "sequence", "frame_id", "class_id", "instance_id", "score".')
	print('\tEach row should correspond to a png file "<sequence>_<frame_id>_<class_id>_<instance_id>.png" depicting an individual instance.')
	pass


def check_inst_submission(path):
	"""Checks if all files required for the submission exist and are in the right format."""

	# check if path contains a predictions.json
	inst_path = path / 'instances.csv'

	print('Checking for "instances.csv" ... ', end='',  flush=True)
	if inst_path.exists():
		print('Ok')		
	else:
		ready_for_submission = False
		print('Missing.')
		print('\tThe file "%s" does not exist. It is required for a submission and should list all predicted instances.' % inst_path)
		_print_inst_format()
		return False, None
	pass

	frames  = _parse_instance_supp(path)
	
	print('Checking for frames ... ', end='',  flush=True)
	missing = [p for f,ps in frames.items() for p in ps if not p.exists()]
		
	if not missing:
		print('Ok')
		return True, frames
	else:
		print('Missing')
		print('\tThere is a mismatch between entries in "instances.csv" and instance masks.')
		print('\tNo masks found for %d instances:' % (len(missing)))
		for f in missing:
			print('\t\t%s' % f)
			pass
		return False, None
	return False, None


def finalize_inst_submission(path, outpath):
	"""Creates a submittable file for semantic class segmentations."""

	ready_for_submission, inst_files = check_inst_submission(path)
	if ready_for_submission:
		print('Preparing submission ...', end='', flush=True)
		
		files = [f for k,v in inst_files.items() for f in v]
		
		submission_path = outpath if outpath is not None else (path / 'inst_submission.zip')
		zip(submission_path, files)
		
		print('Ok')
		print('Submission file is "%s". Please upload it at "https://playing-for-benchmarks.org"' % submission_path)
		pass
	else:
		print('Files are not ready for a submission yet.')
		pass
	return


def check_flow_submission(path):
	"""Checks if all files required for the submission exist and are in the right format."""

	ready_for_submission = True
	ready_for_submission = ready_for_submission and _check_frames(path, [path / (f + '.flo') for f in _get_flow_test_frames()])
	return ready_for_submission


def finalize_flow_submission(path, outpath):
	"""Creates a submittable file for optical flow segmentations."""

	if check_flow_submission(path):
		print('Preparing submission ...', end='', flush=True)
		
		files = [path / (f + '.flo') for f in _get_flow_test_frames()]
		
		submission_path = outpath if outpath is not None else (path / 'flow_submission.bin')
		if encode(submission_path, pathlib.Path('./encode_flow_submission'), path):
			print('Ok')
			print('Submission file is "%s". Please upload it at "https://playing-for-benchmarks.org"' % submission_path)
		else:
			print('Failed')
			print('\tEncoding the submission files failed.')
			pass
		pass
	else:
		print('Files are not ready for a submission yet.')
		pass
	return


def check_depth_submission(path):
	"""Checks if all files required for the submission exist and are in the right format."""

	ready_for_submission = True
	ready_for_submission = ready_for_submission and _check_frames(path, _get_test_frame_paths('.pfm'))
	return ready_for_submission


def finalize_depth_submission(path, outpath):
	"""Creates a submittable file for optical flow segmentations."""

	if check_flow_submission(path):
		print('Preparing submission ...', end='', flush=True)
		
		files = _get_test_frame_paths('.pfm')
		
		submission_path = outpath if outpath is not None else (path / 'depth_submission.bin')
		if encode(submission_path, pathlib.Path('./encode_depth_submission'), path):
			print('Ok')
			print('Submission file is "%s". Please upload it at "https://playing-for-benchmarks.org"' % submission_path)
		else:
			print('Failed')
			print('\tEncoding the submission files failed.')
			pass
		pass
	else:
		print('Files are not ready for a submission yet.')
		pass
	return


def check_pano_submission(path):
	"""Checks if all files required for the submission exist and are in the right format."""

	ready_for_submission = True

	# check if path contains a predictions.json
	json_path = path / 'predictions.json'

	print('Checking for "predictions.json" ... ', end='',  flush=True)
	if json_path.exists():
		print('Ok')
	else:
		ready_for_submission = False
		print('Missing.')
		print('\tThe file "%s" does not exist. It is required for a submission. We are following the COCO Panoptic segmentation format ("http://cocodataset.org/#format-data" (4. Panoptic segmentation)".' % json_path)
		pass
	pass

	ready_for_submission = ready_for_submission and _check_frames(path, _get_test_frame_paths(path, '.png'))
	
	return ready_for_submission


def finalize_pano_submission(path, outpath):
	"""Creates a submittable file for panoptic segmentations."""

	if check_pano_submission(path):
		print('Preparing submission ...', end='', flush=True)
		
		files = [path / 'predictions.json'] + _get_test_frame_paths(path, '.png')
		
		submission_path = outpath if outpath is not None else (path / 'pano_submission.zip')
		zip(submission_path, files)

		print('Ok')
		print('Submission file is "%s". Please upload it at "https://playing-for-benchmarks.org"' % submission_path)
		pass
	else:
		print('Files are not ready for a submission yet.')
		pass
	return


if __name__ == '__main__':

	task2func = {'cls':finalize_cls_submission, 'pano':finalize_pano_submission, 'depth':finalize_depth_submission, 'flow':finalize_flow_submission, 'inst':finalize_inst_submission}

	p = argparse.ArgumentParser('')
	p.add_argument('task', type=str, choices=task2func.keys(), help='Task for which a submission should be prepared.')
	p.add_argument('path', type=pathlib.Path, help='Folder containing all files to be included in the submission.')
	p.add_argument('-o', '--out', type=pathlib.Path, help='Output path to submission file.', default=None)
	args = p.parse_args()

	task2func[args.task](args.path, args.out)
	pass
