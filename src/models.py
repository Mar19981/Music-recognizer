from sqlalchemy import Column, String, Integer, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Association(Base):
    __tablename__ = "associations"
    
    song_id = Column("song", ForeignKey("songs.id"), primary_key=True)
    hash_value = Column("hash", ForeignKey("hashes.hash"), primary_key=True)
    time = Column(Integer, nullable=False)
    
    song = relationship("Song", back_populates="hashes")
    hash = relationship("Hash", back_populates="songs")
    
    def __repr__(self):
        return f"Hash {self.hash_value} Song {self.song_id} Time {self.time}"

class Song(Base):
    __tablename__ = "songs"
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    artist = Column(String)
    album = Column(String)
    
    hashes = relationship("Association", back_populates="song", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"Song {self.id}: {self.artist} - {self.title} from album '{self.album}'"
    
    def __str__(self):
        return f"{self.artist} - {self.title} from album '{self.album}'"

class Hash(Base):
    __tablename__ = "hashes"
    
    hash = Column(Integer, nullable=False, primary_key=True, autoincrement=False)
    
    songs = relationship("Association", back_populates="hash")
    
    def __repr__(self):
        return f"Hash {self.hash}"
    