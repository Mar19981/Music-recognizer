from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Song(Base):
    __tablename__ = "songs"
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    artist = Column(String)
    album = Column(String)
    
    hashes = relationship("Hash", back_populates="song", cascade="all, delete-orphan", lazy=True)
    
    def __repr__(self):
        return f"Song {self.id}: {self.artist} - {self.title} from album '{self.album}'"
    
    def __str__(self):
        return f"{self.artist} - {self.title} from album '{self.album}'"

class Hash(Base):
    __tablename__ = "hashes"
    
    id = Column(Integer, primary_key=True)
    hash = Column(Integer, nullable=False)
    time = Column(Integer, nullable=False)
    song_id = Column(Integer, ForeignKey("songs.id"), nullable=False)
    
    song = relationship("Song", back_populates="hashes")
    
    def __repr__(self):
        return f"Hash {self.hash}: Time: {self.time} SongId {self.song_id}"
    