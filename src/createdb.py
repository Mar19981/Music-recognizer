import os, sys, mutagen, pickle, time, datetime
from recording import Recording
from database import Database
from models import Song, Hash, Association

def createPickleFiles(fileList: list[str]):
    songNameIndex: dict[int, tuple[str, str, str]] = {}
    db: dict[int, list[Tuple[int, int]]] = {}
    for index, file in enumerate(fileList):
        audioFile = mutagen.File(file)
        print(file)
        artist = audioFile["artist"][0] if "artist" in audioFile else input("Artist: ")
        title = audioFile["title"][0] if "title" in audioFile else input("Title: ")
        album = audioFile["album"][0] if "album" in audioFile else input("Album: ")
        songNameIndex[index] = (artist, title, album)
        rec = Recording(duration=0)
        rec.load(file)
        rec.generateHash(id=index)
        for hash, timeIndexPair in rec.fingerprint.items():
            if hash not in db:
                db[hash] = []
            db[hash].append(timeIndexPair)
        print(f"File {index}: {artist} - {album} - {title}")
 
    print("Generating db.pickle file...")
    with open("data/db.pickle", "wb") as dbOutput:
        pickle.dump(db, dbOutput, pickle.HIGHEST_PROTOCOL)
        
    print("Generating songs.pickle file...")
    with open("data/songs.pickle", "wb") as songsOutput:
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
            artist = audioFile["artist"][0], 
            title = audioFile["title"][0], 
            album = audioFile["album"][0] if "album" in audioFile else "",
            hashes = []
            )
        db.addSong(song, rec.fingerprint.items())
        print(f"File {index}: {audioFile["artist"][0]} - {audioFile["album"][0] if "album" in audioFile else ""} - {audioFile["title"][0]}")


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3) or (len(sys.argv) == 3 and sys.argv[2].lower() not in ("pickle", "sql")):
        print("Invalid args!")
        sys.exit(1)
    fileList = []
    for root, _, files in os.walk(sys.argv[1]):
        for file in files:
            if file.endswith(".flac") or file.endswith(".wav") or file.endswith(".mp3"):
                path = os.path.join(root, file)
                fileList.append(path)
               
    if len(fileList) == 0:
        print("Music files not found!")
        sys.exit(1)
    if (not os.path.exists("data") or not os.path.isdir("data")):
        os.mkdir("data")
    start = time.perf_counter()
    arg = sys.argv[2].lower() if len(sys.argv) == 3 else "pickle"
    match(arg):
        case "pickle":
            createPickleFiles(fileList)
        case "sql":
            createSqlDatabase(fileList)
    finish = time.perf_counter()
             
    print(f"Done in {str(datetime.timedelta(seconds = finish - start))}!")