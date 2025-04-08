from typing import Optional

from sqlalchemy import Column, Date, DateTime, Index, Integer, REAL, Table, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import datetime

class Base(DeclarativeBase):
    pass


class AlbumRoots(Base):
    __tablename__ = 'AlbumRoots'
    __table_args__ = (
        UniqueConstraint('identifier', 'specificPath'),
    )

    status: Mapped[int] = mapped_column(Integer)
    type: Mapped[int] = mapped_column(Integer)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    label: Mapped[Optional[str]] = mapped_column(Text)
    identifier: Mapped[Optional[str]] = mapped_column(Text)
    specificPath: Mapped[Optional[str]] = mapped_column(Text)
    caseSensitivity: Mapped[Optional[int]] = mapped_column(Integer)


class Albums(Base):
    __tablename__ = 'Albums'
    __table_args__ = (
        UniqueConstraint('albumRoot', 'relativePath'),
    )

    albumRoot: Mapped[int] = mapped_column(Integer)
    relativePath: Mapped[str] = mapped_column(Text)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    caption: Mapped[Optional[str]] = mapped_column(Text)
    collection: Mapped[Optional[str]] = mapped_column(Text)
    icon: Mapped[Optional[int]] = mapped_column(Integer)
    modificationDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class DownloadHistory(Base):
    __tablename__ = 'DownloadHistory'
    __table_args__ = (
        UniqueConstraint('identifier', 'filename', 'filesize', 'filedate'),
    )

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    identifier: Mapped[Optional[str]] = mapped_column(Text)
    filename: Mapped[Optional[str]] = mapped_column(Text)
    filesize: Mapped[Optional[int]] = mapped_column(Integer)
    filedate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class ImageComments(Base):
    __tablename__ = 'ImageComments'
    __table_args__ = (
        UniqueConstraint('imageid', 'type', 'language', 'author'),
        Index('comments_imageid_index', 'imageid')
    )

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    imageid: Mapped[Optional[int]] = mapped_column(Integer)
    type: Mapped[Optional[int]] = mapped_column(Integer)
    language: Mapped[Optional[str]] = mapped_column(Text)
    author: Mapped[Optional[str]] = mapped_column(Text)
    date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    comment: Mapped[Optional[str]] = mapped_column(Text)


class ImageCopyright(Base):
    __tablename__ = 'ImageCopyright'
    __table_args__ = (
        UniqueConstraint('imageid', 'property', 'value', 'extraValue'),
        Index('copyright_imageid_index', 'imageid')
    )

    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    imageid: Mapped[Optional[int]] = mapped_column(Integer)
    property: Mapped[Optional[str]] = mapped_column(Text)
    value: Mapped[Optional[str]] = mapped_column(Text)
    extraValue: Mapped[Optional[str]] = mapped_column(Text)


class ImageHistory(Base):
    __tablename__ = 'ImageHistory'
    __table_args__ = (
        Index('uuid_index', 'uuid'),
    )

    imageid: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[Optional[str]] = mapped_column(Text)
    history: Mapped[Optional[str]] = mapped_column(Text)


class ImageInformation(Base):
    __tablename__ = 'ImageInformation'
    __table_args__ = (
        Index('creationdate_index', 'creationDate'),
    )

    imageid: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    rating: Mapped[Optional[int]] = mapped_column(Integer)
    creationDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    digitizationDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    orientation: Mapped[Optional[int]] = mapped_column(Integer)
    width: Mapped[Optional[int]] = mapped_column(Integer)
    height: Mapped[Optional[int]] = mapped_column(Integer)
    format: Mapped[Optional[str]] = mapped_column(Text)
    colorDepth: Mapped[Optional[int]] = mapped_column(Integer)
    colorModel: Mapped[Optional[int]] = mapped_column(Integer)


class ImageMetadata(Base):
    __tablename__ = 'ImageMetadata'

    imageid: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    make: Mapped[Optional[str]] = mapped_column(Text)
    model: Mapped[Optional[str]] = mapped_column(Text)
    lens: Mapped[Optional[str]] = mapped_column(Text)
    aperture: Mapped[Optional[float]] = mapped_column(REAL)
    focalLength: Mapped[Optional[float]] = mapped_column(REAL)
    focalLength35: Mapped[Optional[float]] = mapped_column(REAL)
    exposureTime: Mapped[Optional[float]] = mapped_column(REAL)
    exposureProgram: Mapped[Optional[int]] = mapped_column(Integer)
    exposureMode: Mapped[Optional[int]] = mapped_column(Integer)
    sensitivity: Mapped[Optional[int]] = mapped_column(Integer)
    flash: Mapped[Optional[int]] = mapped_column(Integer)
    whiteBalance: Mapped[Optional[int]] = mapped_column(Integer)
    whiteBalanceColorTemperature: Mapped[Optional[int]] = mapped_column(Integer)
    meteringMode: Mapped[Optional[int]] = mapped_column(Integer)
    subjectDistance: Mapped[Optional[float]] = mapped_column(REAL)
    subjectDistanceCategory: Mapped[Optional[int]] = mapped_column(Integer)

class ImageTagProperties(Base):
    __tablename__ = 'ImageTagProperties'
    imageid: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    tagid: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    property: Mapped[Optional[str]] = mapped_column(Text)
    value: Mapped[Optional[str]] = mapped_column(Text)


class ImagePositions(Base):
    __tablename__ = 'ImagePositions'

    imageid: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    latitude: Mapped[Optional[str]] = mapped_column(Text)
    latitudeNumber: Mapped[Optional[float]] = mapped_column(REAL)
    longitude: Mapped[Optional[str]] = mapped_column(Text)
    longitudeNumber: Mapped[Optional[float]] = mapped_column(REAL)
    altitude: Mapped[Optional[float]] = mapped_column(REAL)
    orientation: Mapped[Optional[float]] = mapped_column(REAL)
    tilt: Mapped[Optional[float]] = mapped_column(REAL)
    roll: Mapped[Optional[float]] = mapped_column(REAL)
    accuracy: Mapped[Optional[float]] = mapped_column(REAL)
    description: Mapped[Optional[str]] = mapped_column(Text)



t_ImageProperties = Table(
    'ImageProperties', Base.metadata,
    Column('imageid', Integer, nullable=False),
    Column('property', Text, nullable=False),
    Column('value', Text, nullable=False),
    UniqueConstraint('imageid', 'property')
)


t_ImageRelations = Table(
    'ImageRelations', Base.metadata,
    Column('subject', Integer),
    Column('object', Integer),
    Column('type', Integer),
    UniqueConstraint('subject', 'object', 'type'),
    Index('object_relations_index', 'object'),
    Index('subject_relations_index', 'subject')
)




t_ImageTags = Table(
    'ImageTags', Base.metadata,
    Column('imageid', Integer, nullable=False),
    Column('tagid', Integer, nullable=False),
    UniqueConstraint('imageid', 'tagid'),
    Index('tag_id_index', 'imageid'),
    Index('tag_index', 'tagid')
)


class Images(Base):
    __tablename__ = 'Images'
    __table_args__ = (
        UniqueConstraint('album', 'name'),
        Index('dir_index', 'album'),
        Index('hash_index', 'uniqueHash'),
        Index('image_name_index', 'name')
    )

    name: Mapped[str] = mapped_column(Text)
    status: Mapped[int] = mapped_column(Integer)
    category: Mapped[int] = mapped_column(Integer)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    album: Mapped[Optional[int]] = mapped_column(Integer)
    modificationDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    fileSize: Mapped[Optional[int]] = mapped_column(Integer)
    uniqueHash: Mapped[Optional[str]] = mapped_column(Text)
    manualOrder: Mapped[Optional[int]] = mapped_column(Integer)


class Searches(Base):
    __tablename__ = 'Searches'

    name: Mapped[str] = mapped_column(Text)
    query: Mapped[str] = mapped_column(Text)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    type: Mapped[Optional[int]] = mapped_column(Integer)


t_Settings = Table(
    'Settings', Base.metadata,
    Column('keyword', Text, nullable=False, unique=True),
    Column('value', Text)
)


t_TagProperties = Table(
    'TagProperties', Base.metadata,
    Column('tagid', Integer),
    Column('property', Text),
    Column('value', Text),
    Index('tagproperties_index', 'tagid')
)


class Tags(Base):
    __tablename__ = 'Tags'
    __table_args__ = (
        UniqueConstraint('name', 'pid'),
    )

    name: Mapped[str] = mapped_column(Text)
    id: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    pid: Mapped[Optional[int]] = mapped_column(Integer)
    icon: Mapped[Optional[int]] = mapped_column(Integer)
    iconkde: Mapped[Optional[str]] = mapped_column(Text)


t_TagsTree = Table(
    'TagsTree', Base.metadata,
    Column('id', Integer, nullable=False),
    Column('pid', Integer, nullable=False),
    UniqueConstraint('id', 'pid')
)


class VideoMetadata(Base):
    __tablename__ = 'VideoMetadata'

    imageid: Mapped[Optional[int]] = mapped_column(Integer, primary_key=True)
    aspectRatio: Mapped[Optional[str]] = mapped_column(Text)
    audioBitRate: Mapped[Optional[str]] = mapped_column(Text)
    audioChannelType: Mapped[Optional[str]] = mapped_column(Text)
    audioCompressor: Mapped[Optional[str]] = mapped_column(Text)
    duration: Mapped[Optional[str]] = mapped_column(Text)
    frameRate: Mapped[Optional[str]] = mapped_column(Text)
    exposureProgram: Mapped[Optional[int]] = mapped_column(Integer)
    videoCodec: Mapped[Optional[str]] = mapped_column(Text)
