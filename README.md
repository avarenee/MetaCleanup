# MetaCleanup
A tool for cleaning up your music library

MetaCleanup v1.0
by avarenee
----------------

This is my first little command-line app. I remember when first getting into
music, I got, like, REALLY into music, and I was downloading up to ten new 
albums every day. And when you download music from *cough cough* questionable 
sources, your files are most likely going to have messy and inconsistent tags.
With such a huge music library, the thought of going in and manually fixing the
tags is a pain. Thus, my attempt at coding an autotagger. Currently, the only 
feature is running the python file in the command line with <dir> as the only 
argument, <dir> being the folder where you keep your music folders. So, you 
would enter the directory you save MetaCleanup to in bash, then enter:

$ python3 MetaCleanup.py <dir>

And for each album, the code will:

  1. Create a dictionary based on the album's metadata obtained using mutagen
  2. Search Discogs using data from the dictionary to find the album's page
  3. Using requests_html, parse Discogs to create a new dictionary with correct
     information about the album
  4. Re-tag the album with mutagen using the new dictionary
  5. Rename the files and directories with this data to add consistency to your
     music library
  6. Add album art if the album folder contains none.

Things I will work on to improve this app over time:

- Ability to tag albums that don't have master releases on Discogs

- Better handling of exceptions

- Compatibility with more music filetypes

- Ability to correctly tag soundtracks/VA compilations generally

- Use the Discogs API rather than parsing pages with requests_html, maybe 
  cross-reference searches with other search engine data.

- More user options, perhaps the option for users to verify the Discogs album
  used to re-tag the current album

- Use of jupyter notebook to handle the filesystem operations better  
