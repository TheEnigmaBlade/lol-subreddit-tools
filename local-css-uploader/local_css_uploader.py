#!/usr/bin/env python3

######################
# User configuration #
######################

oauth_public = ""
oauth_secret = ""
username = ""
password = ""
user_agent = "script:Dev CSS uploader:v1.1 (by /u/TheEnigmaBlade), run by /u/{}".format(username)

watch_dir		= ""
main_file		= "theme.less"
include_ext		= ".less"
exclude_files	= None
output_file		= "css/stylesheet.css"
extend_file		= None

use_preprocessor = False
preprocessor_cmd = "lessc \"{in_file}\" \"{out_file}\""

do_upload = True
subreddit = ""
update_cooldown = 10 #sec

##########################################
# DO NOT TOUCH ANYTHING AFTER THIS POINT #
##########################################

import os, time, subprocess
import praw_script_oauth, praw.errors
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

_oauth_scopes={"modconfig"}
_max_stylesheet_size = 128 #KiB

if "SECRET_CONFIG" in os.environ:
	c = __import__(os.environ["SECRET_CONFIG"])
	globals().update({k: c.__dict__[k] for k in c.__dict__ if not k.startswith("_")})

r = None

def init_reddit():
	global r
	if do_upload:
		if r:
			r.clear_authentication()
		r = praw_script_oauth.connect(oauth_public, oauth_secret, username, password, oauth_scopes=_oauth_scopes,
									  useragent=user_agent, script_key="dev_css_{}".format(username))

def update_css():
	# Get CSS to upload (optionally running a preprocessor)
	input_file = os.path.join(watch_dir, main_file)
	if use_preprocessor:
		print("Running preprocessor")
		p = subprocess.Popen(preprocessor_cmd.format(in_file=input_file, out_file=output_file), shell=True, stderr=subprocess.PIPE)
		error = p.stderr.read()
		
		if error and len(error) > 0:
			error = error.decode("utf-8")
			print("Preprocessor failed!", file=sys.stderr)
			print(error, file=sys.stderr)
			return
		
		with open(output_file, "r") as f:
			output = f.read()
	else:
		with open(input_file, "r") as f:
			output = f.read()
	
	# Additional CSS processing
	output = clean_css(output)
	if extend_file:
		with open(extend_file, "r") as f:
			output += f.read()
	
	# Save result
	with open(output_file, "w") as f:
		f.write(output)
	
	if do_upload:
		update_reddit(output)

def clean_css(css):
	css = css.replace("  ", "\t")
	css = css.replace(" 0px", " 0")
	return css

def update_reddit(css):
	print("Uploading to /r/{}".format(subreddit))
	
	# Check stylesheet size rather than relying on Reddit (it's buggy)
	if len(css) > _max_stylesheet_size * 1024:
		print("Can't upload; stylesheet > {} KiB".format(_max_stylesheet_size), file=sys.stderr)
		return
	
	try:
		response = r.set_stylesheet(subreddit, css)
		if "errors" in response and len(response["errors"]) > 0:
			errors = response["errors"]
			print("Failed!")
			print("Error when updating stylesheet", file=sys.stderr)
			print(errors, file=sys.stderr)
		else:
			print("Done!")
	except praw.errors.OAuthInvalidToken:
		print("Failed, retrying...")
		time.sleep(2)
		init_reddit()
		update_reddit(css)

# File change watcher

class FileSaveWatcher(FileSystemEventHandler):
	def __init__(self):
		self.ignores = [os.path.join(watch_dir, p) for p in exclude_files] if exclude_files else []
		self.last_time = 0
	
	def on_any_event(self, event):
		# Check if off cooldown
		curr_time = time.time()
		if curr_time - self.last_time < update_cooldown:
			return
		self.last_time = curr_time
		
		#Check if ignored
		if event.src_path in self.ignores:
			return
		if not event.src_path.endswith(include_ext):
			return
		
		update_css()

def run_file_watcher():
	if not os.path.isdir(watch_dir):
		print("\"{}\" is not a valid directory".format(watch_dir), file=sys.stderr)
		return
	
	observer = Observer()
	observer.schedule(FileSaveWatcher(), watch_dir, recursive=True)
	observer.start()
	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		observer.stop()
	observer.join()

# Main

if __name__ == "__main__":
	init_reddit()
	
	import sys
	if len(sys.argv) == 2 and sys.argv[1] == "--no-watch":
		update_css()
	else:
		run_file_watcher()
