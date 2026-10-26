# ResourceSpace_altFiles

*Python script to rename alternative files regardless of patterns by checking skipped numbering in filenames given a .txt or .csv file; used when uploading digital library collections to ResourceSpace.*

------------
## Requirements:
  1. a folder containing the numbered image files, and
  2. a list of the MAIN (front) filenames (a .txt with one name per line, or a
     .csv whose first column is the filename).

Each prefix group is sorted by number (e.g. name_b2_f2_), Every file that is NOT
in the provided list is treated as an alternative to the main before it. Skipped
files are counted and renamed into -alternative files.

Example, main list = name_b2_f2_001.jpg, name_b2_f2_005.jpg
  name_b2_f2_002.jpg -> name_b2_f2_001-alt.jpg
  name_b2_f2_003.jpg -> name_b2_f2_001-alt2.jpg
  name_b2_f2_004.jpg -> name_b2_f2_001-alt3.jpg
  name_b2_f2_006.jpg -> name_b2_f2_005-alt.jpg (ad nauseam after the last main)

A front/back-only collection (xxx.jpg + one extra file) simply produces xxx-alt.jpg.

## Safety
------
  * Automatically does a dry run. Nothing is renamed until --apply is added
  * Never overwrites an existing file (skips and warns).
  * Warns if a main would end up with more than 9 alts (10 images total max) so that
    a compound can be created instead, and flags files with no main before them.
  * Writes a CSV log of every rename (old name, new name) when --apply is used.

## Usage
-----
  python rename_alt_files.py FOLDER MAIN_LIST.txt            # preview/dry run
  python rename_alt_files.py FOLDER MAIN_LIST.txt --apply    # rename alternative files
