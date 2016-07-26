# Subreddit wiki mover

Selects a random snoo from a folder and uploads to a subreddit. Useful for having rotating snoos.

## Requirements

* Python 3+ (tested on 3.5)

Additional Python requirements are outlined in `requirements.txt`.

## Usage

    python update_snoo.py

Should be set up with a scheduler (ex. cron) to run regularly.

## Configuration

The following settings are available at the top of `wiki_mover.py`.

|Name|Type|Description|Example|
:--|:-:|:--|:--
subreddit|string|Subreddit to which snoo is uploaded (without `/r/`)|`mysubreddit`
snoos_dir|string|Path to the folder containing snoo images|`snoos/`
