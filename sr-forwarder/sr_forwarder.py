#!/usr/bin/env python3

######################
# User configuration #
######################

subreddit = ""
user_exclude = []

slack_webhook = ""
slack_channels = []

user_agent = "script:Subreddit forwarder for Slack:v1.1 (by /u/TheEnigmaBlade), run for /r/{}".format(subreddit)
cache_file = "caches/{}.cache".format(subreddit)

##########################################
# DO NOT TOUCH ANYTHING AFTER THIS POINT #
##########################################

import os

if "SECRET_CONFIG" in os.environ:
	c = __import__(os.environ["SECRET_CONFIG"])
	globals().update({k: c.__dict__[k] for k in c.__dict__ if not k.startswith("_")})

# Main

import requests

def create_post_message(post):
	if not post.is_self or not post.selftext:
		print("Post is not text")
		return None
	
	author = post.author.name.lower()
	if user_exclude and author in user_exclude:
		print("Excluded author")
		return None
	
	link = post.permalink
	title = post.title
	body = post.selftext[:140]
	body = body.replace("\n", " ").replace("  +", " ")
	
	return "_{title}_\n> {body}\n{link}".format(link=link, title=title, body=body)

def send_message(msg):
	if slack_channels and len(slack_channels) > 0:
		for channel in slack_channels:
			print("Test to {}".format(channel))
			#resp = requests.post(slack_webhook, json={"text": msg, "channel": channel})
			#print(resp.status_code, resp.reason)
	else:
		resp = requests.post(slack_webhook, json={"text": msg})
		print(resp.status_code, resp.reason)

import praw
import cache

print("Loading cache")
c = cache.load_cached_storage(cache_file, default_size=30)

print("Connecting to reddit")
r = praw.Reddit(user_agent=user_agent)
sub = r.get_subreddit(subreddit, fetch=False)

print("Getting new")
new = sub.get_new(limit=10)
new = c.get_diff(new)
print("New posts:")
print(new)

for post in new:
	msg = create_post_message(post)
	if msg:
		print()
		print(msg)
		send_message(msg)
