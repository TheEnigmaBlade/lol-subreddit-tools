#!/usr/bin/env python3

######################
# User configuration #
######################

oauth_public = ""
oauth_secret = ""
username = ""
password = ""
user_agent = "script:Snoo updater:v1.1 (by /u/TheEnigmaBlade), run by /u/{}".format(username)

subreddit = ""

snoos_dir = "snoos/"

##########################################
# DO NOT TOUCH ANYTHING AFTER THIS POINT #
##########################################

import os, praw_script_oauth, random

_oauth_scopes = {"modconfig"}

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
		r.upload_image(subreddit, path, header=True)
	except:
		print("Failed to upload sprite image")

def main():
	# Connect to reddit
	r = praw_script_oauth.connect(oauth_public, oauth_secret, username, password,
								  oauth_scopes=_oauth_scopes, useragent=user_agent,
								  script_key="snoo_updater_{}".format(subreddit))
	if r is None:
		print("Failed to create reddit instance")
		return
	
	# Update snoo
	snoo = choose_random_snoo()
	print("Uploading snoo: {}".format(snoo))
	upload_snoo(r, snoo)
	
	print("Done!")
	
if __name__ == "__main__":
	main()
