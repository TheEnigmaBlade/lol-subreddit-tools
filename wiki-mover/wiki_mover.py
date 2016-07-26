#!/usr/bin/env python3

######################
# User configuration #
######################

oauth_public = ""
oauth_secret = ""
username = ""
password = ""
user_agent = "script:Wiki mover:v1.1 (by /u/TheEnigmaBlade), run by /u/{}".format(username)

from_subreddit	= ""
from_path 		= ""
to_subreddit	= ""
to_path			= ""
keep_perms	= False
hide_old	= True
save_info	= True

wiki_reason = ""

##########################################
# DO NOT TOUCH ANYTHING AFTER THIS POINT #
##########################################

import os, praw_script_oauth
from datetime import datetime

_oauth_scopes = {"modwiki", "wikiread", "wikiedit"}

if "SECRET_CONFIG" in os.environ:
	c = __import__(os.environ["SECRET_CONFIG"])
	globals().update({k: c.__dict__[k] for k in c.__dict__ if not k.startswith("_")})

def main():
	# Connect to reddit
	r = praw_script_oauth.connect(oauth_public, oauth_secret, username, password, 
								  oauth_scopes=_oauth_scopes, useragent=user_agent, script_key="wiki_mover_{}".format(username))
	if r is None:
		print("Failed to create reddit instance")
		return
	
	print("Getting wiki page list from {}".format(from_subreddit))
	pages = r.get_wiki_pages(from_subreddit)
	for page in pages:
		old_path = page.page
		if old_path.startswith(from_path):
			print("From: "+old_path)
			key = old_path[len(from_path):]
			#print("  "+key)
			
			print("  Retrieving wiki page content")
			page.refresh()
			
			new_path = os.path.join(to_path, key)
			print("  To: " + new_path)
			content = page.content_md
			if save_info:
				date_info = datetime.utcfromtimestamp(page.revision_date).strftime("%Y-%m-%d %H:%M:%S")
				content = "^(Original URL: /r/{}/wiki/{})  \n^(Last revision: {})\n\n---\n\n".format(from_subreddit, old_path, date_info) + content
			
			print("  Creating new wiki page")
			new_page = r.edit_wiki_page(to_subreddit, new_path, content, reason=wiki_reason)
			
			if keep_perms or hide_old:
				page_settings = page.get_settings()
				if keep_perms and page.permlevel != 0:
					new_page.edit_settings(page_settings["permlevel"], True)
				if hide_old:
					page.edit_settings(page_settings["permlevel"], False)
			
if __name__ == "__main__":
	main()
