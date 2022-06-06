from models import Song, Hash, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

class Database:
    def __init__(self, dbName: str):
        self.__db = create_engine(f"sqlite:///{dbName}", future=True)
        
    def createDatabase(self):
        Base.metadata.drop_all(bind=self.__db)
        Base.metadata.create_all(bind=self.__db)
    
    def addSong(self, song: Song):
        with Session(self.__db) as session:
            session.add(song)
            session.commit()
            
    def getSongs(self):
        with Session(self.__db) as session:
            songs = session.query(Song).all()
        return songs
    