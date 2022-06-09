from models import Song, Hash, Base, Association
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

class Database:
    def __init__(self, dbName: str, e: bool = False):
        self.__db = create_engine(f"sqlite:///{dbName}", future=True, echo=e)
        
    def createDatabase(self):
        Base.metadata.drop_all(bind=self.__db)
        Base.metadata.create_all(bind=self.__db)
    
    def addSong(self, song: Song, hashes):
        with Session(self.__db) as session:
            query = session.query(Hash).all()
            for hash, timeIndexPair in hashes:
                foundHash = list(filter(lambda x: x.hash == hash, query))
                assoc = Association(time=timeIndexPair[0])
                assoc.hash = Hash(hash=hash) if len(foundHash) == 0 else foundHash[0]
                song.hashes.append(assoc)
                    
            session.add(song)
            session.commit()
            
    def getSongs(self):
        with Session(self.__db) as session:
            songs = session.query(Song).all()
        return songs
    
    def getSong(self, id: int):
        with Session(self.__db) as session:
            song = session.get(Song, id)
        return song
    
    def getHashesByValue(self, hash: int):
        with Session(self.__db) as session:
            result = session.get(Hash, hash)
        return result
    
    def getHashes(self):
        with Session(self.__db) as session:
            hashes = session.query(Hash).all()
        return hashes
    