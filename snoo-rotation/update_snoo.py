#!/usr/bin/env python3

######################
# User configuration #
######################

oauth_public = ""
oauth_secret = ""
username = ""
password = ""
user_agent = "script:Snoo updater:v1.2 (by /u/TheEnigmaBlade), run by /u/{}".format(username)

subreddit = ""

snoos_dir = "snoos/"

##########################################
# DO NOT TOUCH ANYTHING AFTER THIS POINT #
##########################################

import os, praw, random

if "SECRET_CONFIG" in os.environ:
	c = __import__(os.environ["SECRET_CONFIG"])
	globals().update({k: c.__dict__[k] for k in c.__dict__ if not k.startswith("_")})

# Main

def choose_random_snoo():
	snoos = os.listdir(snoos_dir)
	snoo = random.choice(snoos)
	return os.path.join(snoos_dir, snoo)

def upload_snoo(r, path):
	try:
		r.subreddit(subreddit).stylesheet.upload_header(path)
	except:
		print("Failed to upload sprite image")

def main():
	# Connect to reddit
	r = praw.Reddit(client_id=oauth_public, client_secret=oauth_secret,
					username=username, password=password,
					user_agent=user_agent,
					check_for_updates=False)
	# Update snoo
	snoo = choose_random_snoo()
	print("Uploading snoo: {}".format(snoo))
	upload_snoo(r, snoo)
	
	print("Done!")
	
if __name__ == "__main__":
	main()
