### Reads dr14 text files and dumps the results into a database. ###

import re
import sqlite3
import os
from os.path import join

# Creates, or opens, a database file called audiopy.sqlite.
# If none exists, creates new tables for artists, albums, DR, and tracks
conn = sqlite3.connect('audiopy.sqlite')
cur = conn.cursor()

cur.executescript('''
CREATE TABLE IF NOT EXISTS Artist (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name    TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS Album (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    artist_id  INTEGER,
    title   TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS DR (
    drval  INTEGER NOT NULL PRIMARY KEY UNIQUE
);

CREATE TABLE IF NOT EXISTS Track (
    id  INTEGER NOT NULL PRIMARY KEY 
        AUTOINCREMENT UNIQUE,
    title TEXT  UNIQUE,
    duration TEXT,
    artist_id INTEGER,
    album_id  INTEGER,
    dr_id INTEGER,
    peak FLOAT,
    rms FLOAT
);
''')

print("""
====================================================
This program will extract data from text files in 
the directory specified by the user.
It will extract the data from those files and enter
them into a sqlite database.
====================================================
""")

#####################################################################
# Checks the user-entered path, if the path does not exist
# the application loops and ask for it again.
# If the path does exist, it searches for all filenames
# ending with 'dr14.txt' and extract the data using regular expressions.
# It then inputs the extracted data into the database tables.
#####################################################################

usrdir = True
while usrdir is True:
    #usrpath = input("Enter the path to your music (i.e. /home/user/Music): ")
    usrpath = "./dr14"
    print(usrpath)
    if len(usrpath) > 1:
        if os.path.isdir(usrpath) is True:
            usrdir = False
        else : print("The path you entered is incorrect.\n\n")
for (dirname, dirs, files) in os.walk(usrpath + '/.'):
   for filename in files:
       if filename.endswith('dr14.txt') :
           drtxt = os.path.join(dirname,filename)
           print("\n\n" + drtxt)
           drtxt = open(drtxt)
           for line in drtxt:
                line.rstrip()
                matchartist = re.findall('^Analyzed:\s(.+ ?)\s/', line)
                matchalbum = re.findall('^Analyzed:\s.+ ?\s/\s(.+ ?)', line)
                matchdr = re.findall('^DR([0-9]*)', line)
                matchtracknum = re.findall('\s([0-9][0-9])-.+', line)
                matchtrack = re.findall('[0-9][0-9]-(.+ ?)\\.?', line)
                matchpeak = re.findall('\s(-.+)\sdB.+\s-', line)
                matchrms = re.findall('dB.+\s(-.+)\sdB.+\s[0-9]', line)
                matchduration = re.findall('\s([0-9]*:.+).+[0-9]', line)
                if len(matchartist) and len(matchalbum) > 0:
                    artist = matchartist[0]
                    album = matchalbum[0]
                    print(artist, "-", album)
                    print("Reading DR text file and writing to database...")
                if len(matchdr) and len(matchtracknum) and len(matchtrack) and\
                 len(matchpeak) and len(matchrms) and len(matchduration) > 0:
                    dr = int(matchdr[0])
                    tracktitle = matchtrack[0]
                    peakval = float(matchpeak[0])
                    rmsval = float(matchrms[0])
                    duration = matchduration[0]
                else:
                    continue
                
                cur.execute('''INSERT OR IGNORE INTO Artist (name) 
                    VALUES ( ? )''', ( artist, ) )
                cur.execute('SELECT id FROM Artist WHERE name = ? ', (artist, ))
                artist_id = cur.fetchone()[0]
                
                cur.execute('''INSERT OR IGNORE INTO Album (title, artist_id) 
                    VALUES ( ?, ? )''', ( album, artist_id ) )
                cur.execute('SELECT id FROM Album WHERE title = ? ', (album, ))
                album_id = cur.fetchone()[0]
                
                cur.execute('''INSERT OR IGNORE INTO DR (drval) 
                    VALUES ( ? )''', ( dr, ) )
                cur.execute('SELECT drval FROM DR WHERE drval = ? ', (dr, ))
                dr_id = cur.fetchone()[0]
                
                cur.execute('''INSERT OR REPLACE INTO Track
                    (title, duration, artist_id, album_id, dr_id, peak, rms) VALUES ( ?, ?, ?, ?, ?, ?, ? )''', 
                    ( tracktitle, duration, artist_id, album_id, dr_id, peakval, rmsval ) )

###############################################################
# Writes/commits the extracted data to the audiopy.sqlite file
# and tells the user the data dump is complete.
###############################################################

conn.commit()
print("\n======================================================\n\nDatabase dump complete.")
