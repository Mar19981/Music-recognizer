import os, sys, mutagen, pickle
from typing import Dict, Tuple, List
from recording import Recording
from database import Database
from models import Song, Hash

def createPickleFiles(fileList: list[str]):
    index = 0
    songNameIndex: Dict[int, Tuple[str, str, str]] = {}
    db: Dict[int, List[Tuple[int, int]]] = {}
    for file in fileList:
        audioFile = mutagen.File(file)
        songNameIndex[index] = (audioFile['artist'][0], audioFile['title'][0], audioFile['album'][0] if 'album' in audioFile else '')
        rec = Recording(duration=0)
        rec.load(file)
        rec.generateHash(id=index)
        for hash, timeIndexPair in rec.fingerprint.items():
            if hash not in db:
                db[hash] = []
            db[hash].append(timeIndexPair)
        print(f"File {index}: {audioFile['artist'][0]} - {audioFile['album'][0] if 'album' in audioFile else ''} - {audioFile['title'][0]}")
        index += 1  
    print("Generating db.pickle file...")
    with open("db.pickle", "wb") as dbOutput:
        pickle.dump(db, dbOutput, pickle.HIGHEST_PROTOCOL)
        
    print("Generating songs.pickle file...")
    with open("songs.pickle", "wb") as songsOutput:
        pickle.dump(songNameIndex, songsOutput, pickle.HIGHEST_PROTOCOL)
    
def createSqlDatabase(fileList: list[str]):
    db = Database("db.db")
    db.createDatabase()
    
    for index, file in enumerate(fileList):
        audioFile = mutagen.File(file)
        rec = Recording(duration=0)
        rec.load(file)
        rec.generateHash(id=index)
        song = Song(
            artist = audioFile['artist'][0], 
            title = audioFile['title'][0], 
            album = audioFile['album'][0] if 'album' in audioFile else '',
            hashes = [Hash(hash=hash, time=timeIndexPair[0]) for hash, timeIndexPair in rec.fingerprint.items()]
            )
        db.addSong(song)
        print(f"File {index}: {audioFile['artist'][0]} - {audioFile['album'][0] if 'album' in audioFile else ''} - {audioFile['title'][0]}")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[2].lower() not in ("pickle", "sql"):
        print("Invalid args!")
        sys.exit(1)
    fileList = []
    for root, _, files in os.walk(sys.argv[1]):
        for file in files:
            if file.endswith(".flac"):
                path = os.path.join(root, file)
                fileList.append(path)
    
    match(sys.argv[2].lower()):
        case "pickle":
            createPickleFiles(fileList)
        case "sql":
            createSqlDatabase(fileList)
            
        
    print("Done!")