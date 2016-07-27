# League of Legends flair and comment icon generator

Generates champion flair, champion comment icons, item comment icons, and summoner spell comment icons using data and images pulled from DDragon. Generated sprite sheets and CSS are uploaded to a subreddit, and markdown tables are saved to a file.

I use it in conjunction with `local-css-updater`, which uses the flair CSS output file as its `extend_file`.

## Requirements

* Python 3.4+ (tested on 3.5)

Additional Python requirements are outlined in `requirements.txt`.

## Usage

    python update_flair.py

## Configuration

The following settings are available at the top of `update_flair.py`.

|Name|Type|Description|Example|
:--|:-:|:--|:--
subreddit|string|Subreddit being updated (without `/r/`).|`"mysubreddit"`
sprite_dir|string|Path to folder containing downloaded and generated sprite sheets.|`"sprites/"`
css_dir|string|Path to folder containing generated CSS and markdown.|`"css/"`
|||
configs|list(dict)|DDragon associations and generated data specifications.|
|||
stylesheet_inject_mark|string|Denotes the start of auto-generated CSS in a subreddit stylesheet.|`"#*/"`
stylesheet_inject_default|string|Default marker for auto-generated CSS added if one isn't found. Should end with `stylesheet_inject_mark`.|`"/*# AUTO-GENERATED AFTER THIS POINT #*/"`
stylesheet_new_file|string|File to which generated CSS is saved.|`"flair.css"`
stylesheet_file|string|File to which the modified stylesheet from `subreddit` is saved.|`"stylesheet.css"`
stylesheet_update|bool|If `True`, generated sprite sheets and CSS are uploaded to Reddit.|
stylesheet_max_size|int|Maximum size of the stylesheet, in KiB. Don't change this unless you're weird.|128
stylesheet_image_max_size|int|Maximum size of sprite sheets, in KiB. Don't change this unless you're weird.|500
|||
md_header|string|Header of generated markdown tables|`"|Name|Code|Preview|\n|:--|:--|:-:|\n"`
