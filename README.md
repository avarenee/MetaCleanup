# MetaCleanup
A tool for cleaning up your music library

MetaCleanup v1.05
by avarenee
----------------

This is my first little command-line app. I remember when first getting into
music, I got, like, REALLY into music, and I was downloading up to ten new 
albums every day. And when you download music from *cough cough* questionable 
sources, your files are most likely going to have messy and inconsistent tags.
With such a huge music library, the thought of going in and manually fixing the
tags is a pain. Thus, my attempt at coding an autotagger. Currently, the only 
feature is running the python file in the command line with \<dir\> as the only 
argument, \<dir\> being the folder where you keep your album folders. So, you 
would enter the directory you save MetaCleanup to in bash, then enter:

```sh
$ pip install -r requirements
$ cd MetaCleanup
$ python3 MetaCleanup.py <dir> <key>
```
  
Where \<key\> is your Discogs API key

And for each album, the code will:

  1. Search Discogs using tagging data to find the album's page
  2. Re-tag the album with mutagen using the Discogs data
  3. Rename the files and directories with this data to add consistency to your
     music library
  4. Add album art if the album folder contains none.

Things I will work on to improve this app over time:

- Better handling of exceptions

- Compatibility with more music filetypes

- Implement a timer so requests don't time out

- More user options, perhaps the option for users to verify the Discogs album
  used to re-tag the current album
