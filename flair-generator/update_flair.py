#!/usr/bin/env python3

######################
# User configuration #
######################

oauth_public = ""
oauth_secret = ""
username = ""
password = ""
user_agent = "script:League of Legends flair generator:v1.1 (by /u/TheEnigmaBlade), run by /u/{}".format(username)

subreddit = ""
sprite_dir = "sprites/"
css_dir = "css/"

configs = [
	{
		"enabled": True,
		"cdn_key": "champion",
		
		"sprite_name":	 "champions.png",
		"expected_size": 48,
		"save_size":	 24,
		
		"css_file":		"champion-flair.css",
		"css_template":	".flair-{name}::before,a[href=\"#c-{name}\"]{{background-position:-{x}px -{y}px}}",
		"css_padding":	(1, 3),
		
		"md_file":		"champions.md",
		"md_template":	"{name}|`[](#c-{key})`|[](#c-{key})",
		
		"stylesheet_sprite_name": "champion-flair",
	},
	{
		"enabled": True,
		"cdn_key": "summoner",
		
		"sprite_name":	 "summoners.png",
		"expected_size": 48,
		"save_size":	 24,
		
		"css_file":		"summoner-flair.css",
		"css_template":	"a[href=\"#ss-{name}\"]{{background-position:-{x}px -{y}px}}",
		"css_padding":	(0, 0),
		
		"md_file":		"summoners.md",
		"md_template":	"{name}|`[](#ss-{key})`|[](#ss-{key})",
		
		"stylesheet_sprite_name": "summoner-flair"
	},
	{
		"enabled": True,
		"cdn_key": "item",
		"cdn_exclude": "(^tower|quick charge|inactive|disabled|Siege Weapon Slot)",
		
		"sprite_name":	 "items.png",
		"expected_size": 48,
		"save_size":	 24,
		
		"css_file":		"item-flair.css",
		"css_template":	"a[href=\"#i-{name}\"]{{background-position:-{x}px -{y}px}}",
		"css_padding":	(0, 0),
		
		"md_file":		"items.md",
		"md_template":	"{name}|`[](#i-{key})`|[](#i-{key})",
		
		"stylesheet_sprite_name": "item-flair"
	}
]

stylesheet_inject_mark = "#*/"
stylesheet_inject_default = "/*# AUTO-GENERATED AFTER THIS POINT - DO NOT EDIT #*/"
stylesheet_new_file = "flair.css"
stylesheet_file = "stylesheet.css"

stylesheet_update = True
stylesheet_max_size = 128		# KiB
stylesheet_image_max_size = 500	# KiB

md_header = "|Name|Code|Preview|\n|:--|:--|:-:|\n"

##########################################
# DO NOT TOUCH ANYTHING AFTER THIS POINT #
##########################################

import os

if "SECRET_CONFIG" in os.environ:
	c = __import__(os.environ["SECRET_CONFIG"])
	globals().update({k: c.__dict__[k] for k in c.__dict__ if not k.startswith("_")})

# DDragon access

ddragon_base = "http://ddragon.leagueoflegends.com"
realm_request = "/realms/{region}.json"
sprite_cdn_request = "/{realm_ver}/img/sprite/{name}"
data_cdn_request = "/{realm_ver}/data/en_US/{key}.json"

import requests, shutil, re
from functools import lru_cache

def get_ddragon(path, args=None):
	print("GET to DDragon: {}".format(path))
	
	# Execute request
	try:
		getted = requests.get(ddragon_base+path, params=args, headers={"user-agent": user_agent})
		if getted.status_code != requests.codes.ok:
			return None
		return getted.json()
	except Exception as e:
		print("Error: Unknown exception, {}".format(e))
		return None

def get_ddragon_cdn(region, path, args=None, return_type="json", stream=False):
	print("GET to DDragon CDN: {}".format(path))
	
	cdn = get_realm_value(region, "cdn")
	
	# Execute request
	try:
		getted = requests.get(cdn+path, params=args, headers={"user-agent": user_agent}, stream=stream)
		if getted.status_code != requests.codes.ok:
			return None
		
		if return_type == "json":
			return getted.json()
		elif return_type == "raw":
			getted.raw.decode_content = True
			return getted.raw
		return getted
	except Exception as e:
		print("Error: Unknown exception, {}".format(e))
		return None

@lru_cache(maxsize=8)
def get_realm(region):
	return get_ddragon(realm_request.format(region=region))

@lru_cache(maxsize=4)
def get_realm_value(region, name):
	realm = get_realm(region)
	if name in realm:
		return realm[name]
	if name in realm["n"]:
		return realm["n"][name]
	return None

def get_cdn_data(region, key):
	ver = get_realm_value(region, key)
	things = get_ddragon_cdn(region, data_cdn_request.format(realm_ver=ver, key=key))
	if things and "data" in things:
		return things["data"]
	return None

_sprite_name_stripper = re.compile("[\W_]+")

def extract_sprite_data(things, key=lambda x: x["name"].lower(), exclude=None):
	if exclude:
		exclude = re.compile(exclude, re.I)
	
	new_data = dict()
	sprites = set()
	for name in things:
		thing = things[name]
		thing_key = _sprite_name_stripper.sub("", key(thing))
		if len(thing_key) == 0:
			continue
		thing_name = thing["name"]
		if exclude and exclude.search(thing_name):
			continue
		
		image_data = thing["image"]
		sprite = image_data["sprite"]
		if sprite not in sprites:
			sprites.add(sprite)
		new_data[thing_key] = {
			"name": thing_name,
			"sprite": sprite,
			"x": image_data["x"],
			"y": image_data["y"],
			"w": image_data["w"],
			"h": image_data["h"]
		}
	return new_data, sprites

def download_sprite(region, category, name, save_dir):
	ver = get_realm_value(region, category)
	raw = get_ddragon_cdn(region, sprite_cdn_request.format(realm_ver=ver, name=name), return_type="raw", stream=True)
	
	file_path = os.path.join(save_dir, name)
	with open(file_path, "wb") as f:
		shutil.copyfileobj(raw, f)
	
	return file_path

# Image manipulation

from PIL import Image

def combine_sprites(sprite_files, out_file, scale):
	sprites = list()
	sprite_offsets = [0]
	max_width = 0
	
	for sprite_file in sprite_files:
		img = Image.open(sprite_file)
		sprites.append(img)
		sprite_offsets.append(sprite_offsets[-1] + img.size[1])
		max_width = max(max_width, img.size[0])
	
	width = max_width
	height = sprite_offsets[-1]
	combined = Image.new("RGB", (width, height))
	for i, sprite in enumerate(sprites):
		combined.paste(sprite, (0, sprite_offsets[i]))
	
	new_width = int(width * scale)
	new_height = int(height * scale)
	combined = combined.resize((new_width, new_height), resample=Image.ANTIALIAS)
	combined.save(out_file)
	
	return sprite_offsets

# Main

import praw_script_oauth

_oauth_scopes = {"identity", "modconfig"}

def generate_css(config, data, sprites, sprite_offsets, scale):
	def s(val):
		return int(val * scale)
	
	css = ""
	for name in sorted(list(data.keys())):
		data_thing = data[name]
		sprite_offset = sprite_offsets[sprites.index(data_thing["sprite"])]
		template = config["css_template"]
		padding = config["css_padding"]
		css += template.format(name=name.lower(), x=s(data_thing["x"]) + padding[0], y=s(data_thing["y"]+sprite_offset) + padding[1]) + "\n"
	return css

def write_css_file(filename, css):
	os.makedirs(css_dir, exist_ok=True)
	css_path = os.path.join(css_dir, filename)
	with open(css_path, "w") as f:
		f.write(css)

def read_css_file(filename):
	css_path = os.path.join(css_dir, filename)
	try:
		with open(css_path, "r") as f:
			css = f.read().strip()
			return css
	except:
		return None

def generate_markdown(config, data):
	md = md_header
	for name in sorted(list(data.keys())):
		data_thing = data[name]
		md += config["md_template"].format(key=name, name=data_thing["name"]) + "\n"
	return md

def main():
	# Pull data and generate CSS
	new_css = ""
	new_sprite_paths = dict()
	
	for config in configs:
		if not config["enabled"]:
			continue
		
		# Get sprite data
		key = config["cdn_key"]
		data = get_cdn_data("na", key)
		if not data or len(data) == 0:
			print("Failed to get data \"{}\"".format(key))
			return
		data, sprites = extract_sprite_data(data, exclude=config["cdn_exclude"] if "cdn_exclude" in config else None)
		print(sprites)
		
		# Download sprites
		os.makedirs(sprite_dir, exist_ok=True)
		sprites = sorted(list(sprites))
		sprite_paths = list()
		for sprite in sprites:
			path = download_sprite("na", key, sprite, sprite_dir)
			sprite_paths.append(path)
		print(sprite_paths)
		
		# Combined sprites into single image, get section offsets
		scale = config["save_size"] / config["expected_size"]
		combined_sprite_path = os.path.join(sprite_dir, config["sprite_name"])
		sprite_offsets = combine_sprites(sprite_paths, combined_sprite_path, scale)
		print(sprite_offsets)
		
		# Generate CSS
		print("Generating CSS")
		thing_css = generate_css(config, data, sprites, sprite_offsets, scale)
		if not thing_css:
			print("  No CSS generated")
			config["enabled"] = False
			continue
		
		# Compare new CSS with old
		old_thing_css = read_css_file(config["css_file"])
		if old_thing_css and thing_css == old_thing_css:
			print("  CSS not different")
			config["enabled"] = False
			continue
		
		# Save results
		print("  Saving result")
		new_css += thing_css
		new_sprite_paths[config["stylesheet_sprite_name"]] = combined_sprite_path
		write_css_file(config["css_file"], thing_css)
		
		# Generate markdown
		print("Generating markdown")
		thing_md = generate_markdown(config, data)
		write_css_file(config["md_file"], thing_md)
	
	# Check if flair has changed
	if not new_css:
		print("No CSS generated")
		return
	
	# Save flair CSS
	write_css_file(stylesheet_new_file, new_css)
	
	# Connect to reddit
	r = praw_script_oauth.connect(oauth_public, oauth_secret, username, password, oauth_scopes=_oauth_scopes,
								  useragent=user_agent, script_key="flair_{}".format(subreddit))
	
	# Get stylesheet
	print("Updating stylesheet")
	print("  Retrieving...")
	stylesheet = r.get_stylesheet(subreddit)
	if stylesheet is None or "stylesheet" not in stylesheet:
		print("Failed to get stylesheet")
		return
	stylesheet = stylesheet["stylesheet"]
	
	# Inject new CSS into stylesheet
	print("  Injecting new CSS")
	end = stylesheet.find(stylesheet_inject_mark)
	if end != -1:
		end += len(stylesheet_inject_mark)
		stylesheet = stylesheet[:end]
	else:
		stylesheet += "\n" + stylesheet_inject_default
	stylesheet += "\n" + new_css
	print("  Writing to file")
	write_css_file(stylesheet_file, stylesheet)
	
	# Set stylesheet
	if stylesheet_update:
		print("  Updating on /r/{}".format(subreddit))
		print("    Uploading images")
		for stylesheet_sprite_name in new_sprite_paths.keys():
			sprite_path = new_sprite_paths[stylesheet_sprite_name]
			print("      {}".format(stylesheet_sprite_name, sprite_path))
			
			file_size = os.path.getsize(sprite_path)
			if file_size > stylesheet_image_max_size*1024:
				print("      Greater than {} KiB ({:#.2} KiB)".format(stylesheet_image_max_size, file_size/1024))
				print("      Failed to upload sprite image")
				continue
			try:
				r.upload_image(subreddit, sprite_path, name=stylesheet_sprite_name)
			except:
				print("      Failed to upload sprite image")
		
		print("    Updating stylesheet")
		if len(stylesheet) > stylesheet_max_size*1024:
			print("      Greater than {} KiB ({:#.2} KiB)".format(stylesheet_max_size, len(stylesheet) / 1024))
			print("      Failed to update stylesheet")
		else:
			response = r.set_stylesheet(subreddit, stylesheet)
			print(response)
			if "errors" in response and len(response["errors"]) > 0:
				print("Failed to update stylesheet")
				print(response["errors"])
	
	print("Done!")

if __name__ == "__main__":
	main()
