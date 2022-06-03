import os, sys, mutagen, pickle
from typing import Dict, Tuple, List
from recording import Recording



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Invalid args!")
        sys.exit(1)
    index = 0
    songNameIndex: Dict[int, Tuple[str, str, str]] = {}
    db: Dict[int, List[Tuple[str, str, str]]] = {}
    for root, _, files in os.walk(sys.argv[1]):
        for file in files:
            if file.endswith(".flac"):
                path = os.path.join(root, file)
                print(path)
                audioFile = mutagen.File(path)
                print(f"{index} {audioFile['artist'][0]} - {audioFile['album'][0] if 'album' in audioFile else ''} - {audioFile['title'][0]}")
                songNameIndex[index] = (audioFile['artist'][0], audioFile['title'][0], audioFile['album'][0] if 'album' in audioFile else '')
                rec = Recording(duration=0)
                rec.load(path)
                rec.generateHash(id=index)
                for hash, timeIndexPair in rec.fingerprint.items():
                    if hash not in db:
                        db[hash] = []
                    db[hash].append(timeIndexPair)
                index += 1
    with open("db.pickle", "wb") as dbOutput:
        pickle.dump(db, dbOutput, pickle.HIGHEST_PROTOCOL)
    with open("songs.pickle", "wb") as songsOutput:
        pickle.dump(songNameIndex, songsOutput, pickle.HIGHEST_PROTOCOL)
    