from typing import Any, List, Optional

from sqlalchemy import Column, DECIMAL, DateTime, Double, ForeignKeyConstraint, Index, String, Table, Text, VARBINARY, text
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, LONGBLOB, LONGTEXT, SMALLINT, TINYINT, TINYTEXT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import NullType
import datetime
import decimal

class Base(DeclarativeBase):
    pass


class MemoriesPlanetGeometry(Base):
    __tablename__ = 'memories_planet_geometry'
    __table_args__ = (
        Index('planet_osm_id_idx', 'osm_id'),
        Index('planet_osm_polygon_geometry_idx', 'geometry')
    )

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    poly_id: Mapped[str] = mapped_column(String(32))
    type_id: Mapped[int] = mapped_column(INTEGER(11))
    osm_id: Mapped[int] = mapped_column(INTEGER(11))
    geometry: Mapped[Any] = mapped_column(Text)



class OcCollresAccesscache(Base):
    __tablename__ = 'oc_collres_accesscache'
    __table_args__ = (
        Index('collres_user_res', 'user_id', 'resource_type', 'resource_id'),
    )

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    collection_id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True, server_default=text('0'))
    resource_type: Mapped[str] = mapped_column(String(64), primary_key=True, server_default=text("''"))
    resource_id: Mapped[str] = mapped_column(String(64), primary_key=True, server_default=text("''"))
    access: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text('0'))


class OcCollresCollections(Base):
    __tablename__ = 'oc_collres_collections'

    id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(64))


class OcCollresResources(Base):
    __tablename__ = 'oc_collres_resources'

    collection_id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True)
    resource_type: Mapped[str] = mapped_column(String(64), primary_key=True)
    resource_id: Mapped[str] = mapped_column(String(64), primary_key=True)



class OcFacerecogFaces(Base):
    __tablename__ = 'oc_facerecog_faces'
    __table_args__ = (
        Index('faces_image_idx', 'image'),
        Index('faces_person_idx', 'person')
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True, autoincrement=True)
    image: Mapped[int] = mapped_column(BIGINT(20))
    confidence: Mapped[decimal.Decimal] = mapped_column(Double(asdecimal=True))
    landmarks: Mapped[str] = mapped_column(LONGTEXT, comment='(DC2Type:json)')
    descriptor: Mapped[str] = mapped_column(LONGTEXT, comment='(DC2Type:json)')
    creation_time: Mapped[datetime.datetime] = mapped_column(DateTime)
    x: Mapped[int] = mapped_column(INTEGER(11))
    y: Mapped[int] = mapped_column(INTEGER(11))
    width: Mapped[int] = mapped_column(INTEGER(11))
    height: Mapped[int] = mapped_column(INTEGER(11))
    person: Mapped[Optional[int]] = mapped_column(INTEGER(11))
    is_groupable: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text('1'))


class OcFacerecogImages(Base):
    __tablename__ = 'oc_facerecog_images'
    __table_args__ = (
        Index('images_file_idx', 'file'),
        Index('images_model_idx', 'model'),
        Index('images_user_idx', 'user')
    )

    id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True, autoincrement=True)
    user: Mapped[str] = mapped_column(String(64))
    file: Mapped[int] = mapped_column(BIGINT(20))
    model: Mapped[int] = mapped_column(INTEGER(11))
    is_processed: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text('0'))
    error: Mapped[Optional[str]] = mapped_column(String(1024))
    last_processed_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    processing_duration: Mapped[Optional[int]] = mapped_column(BIGINT(20))


class OcFacerecogModels(Base):
    __tablename__ = 'oc_facerecog_models'

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    description: Mapped[Optional[str]] = mapped_column(String(1024))


class OcFacerecogPersons(Base):
    __tablename__ = 'oc_facerecog_persons'
    __table_args__ = (
        Index('persons_user_idx', 'user'),
    )

    id: Mapped[int] = mapped_column(INTEGER(10), primary_key=True, autoincrement=True)
    user: Mapped[str] = mapped_column(String(64))
    name: Mapped[Optional[str]] = mapped_column(String(256))
    is_visible: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text('1'))
    is_valid: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text('0'))
    last_generation_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    linked_user: Mapped[Optional[str]] = mapped_column(String(64))


class OcFileMetadata(Base):
    __tablename__ = 'oc_file_metadata'

    id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True)
    group_name: Mapped[str] = mapped_column(String(50), primary_key=True)
    value: Mapped[Optional[str]] = mapped_column(LONGTEXT)


class OcFilecache(Base):
    __tablename__ = 'oc_filecache'
    __table_args__ = (
        Index('fs_id_storage_size', 'fileid', 'storage', 'size'),
        Index('fs_mtime', 'mtime'),
        Index('fs_name_hash', 'name'),
        Index('fs_parent', 'parent'),
        Index('fs_parent_name_hash', 'parent', 'name'),
        Index('fs_size', 'size'),
        Index('fs_storage_mimepart', 'storage', 'mimepart'),
        Index('fs_storage_mimetype', 'storage', 'mimetype'),
        Index('fs_storage_path_hash', 'storage', 'path_hash', unique=True),
        Index('fs_storage_path_prefix', 'storage', 'path'),
        Index('fs_storage_size', 'storage', 'size', 'fileid'),
        Index('memories_parent_mimetype', 'parent', 'mimetype')
    )

    fileid: Mapped[int] = mapped_column(BIGINT(20), primary_key=True)
    storage: Mapped[int] = mapped_column(BIGINT(20), server_default=text('0'))
    path_hash: Mapped[str] = mapped_column(String(32), server_default=text("''"))
    parent: Mapped[int] = mapped_column(BIGINT(20), server_default=text('0'))
    mimetype: Mapped[int] = mapped_column(BIGINT(20), server_default=text('0'))
    mimepart: Mapped[int] = mapped_column(BIGINT(20), server_default=text('0'))
    size: Mapped[int] = mapped_column(BIGINT(20), server_default=text('0'))
    mtime: Mapped[int] = mapped_column(BIGINT(20), server_default=text('0'))
    storage_mtime: Mapped[int] = mapped_column(BIGINT(20), server_default=text('0'))
    encrypted: Mapped[int] = mapped_column(INTEGER(11), server_default=text('0'))
    unencrypted_size: Mapped[int] = mapped_column(BIGINT(20), server_default=text('0'))
    path: Mapped[Optional[str]] = mapped_column(String(4000))
    name: Mapped[Optional[str]] = mapped_column(String(250))
    etag: Mapped[Optional[str]] = mapped_column(String(40))
    permissions: Mapped[Optional[int]] = mapped_column(INTEGER(11), server_default=text('0'))
    checksum: Mapped[Optional[str]] = mapped_column(String(255))


class OcFilecacheExtended(Base):
    __tablename__ = 'oc_filecache_extended'
    __table_args__ = (
        Index('fce_ctime_idx', 'creation_time'),
        Index('fce_utime_idx', 'upload_time')
    )

    fileid: Mapped[int] = mapped_column(BIGINT(20), primary_key=True)
    creation_time: Mapped[int] = mapped_column(BIGINT(20), server_default=text('0'))
    upload_time: Mapped[int] = mapped_column(BIGINT(20), server_default=text('0'))
    metadata_etag: Mapped[Optional[str]] = mapped_column(String(40))


class OcFilesMetadata(Base):
    __tablename__ = 'oc_files_metadata'
    __table_args__ = (
        Index('files_meta_fileid', 'file_id', unique=True),
    )

    id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True)
    file_id: Mapped[int] = mapped_column(BIGINT(20))
    json: Mapped[str] = mapped_column(LONGTEXT)
    sync_token: Mapped[str] = mapped_column(String(15))
    last_update: Mapped[datetime.datetime] = mapped_column(DateTime)


class OcFilesMetadataIndex(Base):
    __tablename__ = 'oc_files_metadata_index'
    __table_args__ = (
        Index('f_meta_index', 'file_id', 'meta_key', 'meta_value_string'),
        Index('f_meta_index_i', 'file_id', 'meta_key', 'meta_value_int')
    )

    id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True)
    file_id: Mapped[int] = mapped_column(BIGINT(20))
    meta_key: Mapped[Optional[str]] = mapped_column(String(31))
    meta_value_string: Mapped[Optional[str]] = mapped_column(String(63))
    meta_value_int: Mapped[Optional[int]] = mapped_column(BIGINT(20))


class OcFilesReminders(Base):
    __tablename__ = 'oc_files_reminders'
    __table_args__ = (
        Index('reminders_uniq_idx', 'user_id', 'file_id', 'due_date', unique=True),
    )

    id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64))
    file_id: Mapped[int] = mapped_column(BIGINT(20))
    due_date: Mapped[datetime.datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    notified: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text('0'))


class OcFilesTrash(Base):
    __tablename__ = 'oc_files_trash'
    __table_args__ = (
        Index('id_index', 'id'),
        Index('timestamp_index', 'timestamp'),
        Index('user_index', 'user')
    )

    auto_id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True)
    id: Mapped[str] = mapped_column(String(250), server_default=text("''"))
    user: Mapped[str] = mapped_column(String(64), server_default=text("''"))
    timestamp: Mapped[str] = mapped_column(String(12), server_default=text("''"))
    location: Mapped[str] = mapped_column(String(512), server_default=text("''"))
    type: Mapped[Optional[str]] = mapped_column(String(4))
    mime: Mapped[Optional[str]] = mapped_column(String(255))
    deleted_by: Mapped[Optional[str]] = mapped_column(String(64))


class OcFilesVersions(Base):
    __tablename__ = 'oc_files_versions'
    __table_args__ = (
        Index('files_versions_uniq_index', 'file_id', 'timestamp', unique=True),
    )

    id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True)
    file_id: Mapped[int] = mapped_column(BIGINT(20))
    timestamp: Mapped[int] = mapped_column(BIGINT(20))
    size: Mapped[int] = mapped_column(BIGINT(20))
    mimetype: Mapped[int] = mapped_column(BIGINT(20))
    metadata_: Mapped[str] = mapped_column('metadata', LONGTEXT, comment='(DC2Type:json)')


class OcKnownUsers(Base):
    __tablename__ = 'oc_known_users'
    __table_args__ = (
        Index('ku_known_to', 'known_to'),
        Index('ku_known_user', 'known_user')
    )

    id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True)
    known_to: Mapped[str] = mapped_column(String(255))
    known_user: Mapped[str] = mapped_column(String(255))


class OcLoginAddress(Base):
    __tablename__ = 'oc_login_address'

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    uid: Mapped[str] = mapped_column(String(64))
    ip: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[int] = mapped_column(INTEGER(11))


class OcLoginFlowV2(Base):
    __tablename__ = 'oc_login_flow_v2'
    __table_args__ = (
        Index('login_token', 'login_token', unique=True),
        Index('poll_token', 'poll_token', unique=True),
        Index('timestamp', 'timestamp')
    )

    id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True)
    timestamp: Mapped[int] = mapped_column(BIGINT(20))
    started: Mapped[int] = mapped_column(SMALLINT(5), server_default=text('0'))
    poll_token: Mapped[str] = mapped_column(String(255))
    login_token: Mapped[str] = mapped_column(String(255))
    public_key: Mapped[str] = mapped_column(LONGTEXT)
    private_key: Mapped[str] = mapped_column(LONGTEXT)
    client_name: Mapped[str] = mapped_column(String(255))
    login_name: Mapped[Optional[str]] = mapped_column(String(255))
    server: Mapped[Optional[str]] = mapped_column(String(255))
    app_password: Mapped[Optional[str]] = mapped_column(String(1024))


class OcLoginIpsAggregated(Base):
    __tablename__ = 'oc_login_ips_aggregated'
    __table_args__ = (
        Index('UNIQ_FE7C6806539B0606A5E3B32D', 'uid', 'ip', unique=True),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    uid: Mapped[str] = mapped_column(String(64))
    ip: Mapped[str] = mapped_column(String(64))
    seen: Mapped[int] = mapped_column(INTEGER(11))
    first_seen: Mapped[int] = mapped_column(INTEGER(11))
    last_seen: Mapped[int] = mapped_column(INTEGER(11))



class OcMemories(Base):
    __tablename__ = 'oc_memories'
    __table_args__ = (
        Index('memories_dayid_index', 'dayid'),
        Index('memories_fileid_index', 'fileid', unique=True),
        Index('memories_isvideo_idx', 'isvideo'),
        Index('memories_lat_lon_index', 'lat', 'lon'),
        Index('memories_mapcluster_index', 'mapcluster'),
        Index('memories_objectid_index', 'objectid'),
        Index('memories_pdf_idx', 'parent', 'dayid', 'fileid')
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    fileid: Mapped[int] = mapped_column(BIGINT(20))
    dayid: Mapped[int] = mapped_column(INTEGER(11))
    mtime: Mapped[int] = mapped_column(BIGINT(20))
    w: Mapped[int] = mapped_column(INTEGER(11), server_default=text('0'))
    h: Mapped[int] = mapped_column(INTEGER(11), server_default=text('0'))
    objectid: Mapped[str] = mapped_column(String(64), server_default=text("'0'"))
    video_duration: Mapped[int] = mapped_column(INTEGER(11), server_default=text('0'))
    epoch: Mapped[int] = mapped_column(BIGINT(20), server_default=text('0'))
    parent: Mapped[int] = mapped_column(BIGINT(20), server_default=text('0'))
    datetaken: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    isvideo: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text('0'))
    exif: Mapped[Optional[str]] = mapped_column(Text)
    liveid: Mapped[Optional[str]] = mapped_column(String(128), server_default=text("''"))
    orphan: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text('0'))
    lat: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(8, 6))
    lon: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(9, 6))
    mapcluster: Mapped[Optional[int]] = mapped_column(INTEGER(11))
    buid: Mapped[Optional[str]] = mapped_column(String(32), server_default=text("''"))


class OcMemoriesCovers(Base):
    __tablename__ = 'oc_memories_covers'
    __table_args__ = (
        Index('memories_covers_gidx', 'uid', 'clustertype', 'clusterid', unique=True),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    uid: Mapped[str] = mapped_column(String(64))
    clustertype: Mapped[str] = mapped_column(String(64))
    clusterid: Mapped[int] = mapped_column(BIGINT(20))
    objectid: Mapped[int] = mapped_column(BIGINT(20))
    fileid: Mapped[int] = mapped_column(BIGINT(20))
    timestamp: Mapped[int] = mapped_column(BIGINT(20))
    auto: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text('1'))


class OcMemoriesFailures(Base):
    __tablename__ = 'oc_memories_failures'
    __table_args__ = (
        Index('memories_fail_fid_mt_idx', 'fileid', 'mtime'),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    fileid: Mapped[int] = mapped_column(BIGINT(20))
    mtime: Mapped[int] = mapped_column(BIGINT(20))
    reason: Mapped[Optional[str]] = mapped_column(LONGTEXT)


class OcMemoriesLivephoto(Base):
    __tablename__ = 'oc_memories_livephoto'
    __table_args__ = (
        Index('memories_lp_fileid_index', 'fileid', unique=True),
        Index('memories_lp_liveid_index', 'liveid')
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    liveid: Mapped[str] = mapped_column(String(128))
    fileid: Mapped[int] = mapped_column(BIGINT(20))
    mtime: Mapped[int] = mapped_column(BIGINT(20))
    orphan: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text('0'))


class OcMemoriesMapclusters(Base):
    __tablename__ = 'oc_memories_mapclusters'
    __table_args__ = (
        Index('memories_clst_ll_idx', 'lat', 'lon'),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    point_count: Mapped[int] = mapped_column(INTEGER(11))
    lat_sum: Mapped[Optional[decimal.Decimal]] = mapped_column(Double(asdecimal=True))
    lon_sum: Mapped[Optional[decimal.Decimal]] = mapped_column(Double(asdecimal=True))
    lat: Mapped[Optional[decimal.Decimal]] = mapped_column(Double(asdecimal=True))
    lon: Mapped[Optional[decimal.Decimal]] = mapped_column(Double(asdecimal=True))
    last_update: Mapped[Optional[int]] = mapped_column(INTEGER(11))


class OcMemoriesPlaces(Base):
    __tablename__ = 'oc_memories_places'
    __table_args__ = (
        Index('memories_places_fileid_index', 'fileid'),
        Index('memories_places_id_mk_idx', 'osm_id', 'mark'),
        Index('memories_places_osm_id_index', 'osm_id')
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    fileid: Mapped[int] = mapped_column(BIGINT(20))
    osm_id: Mapped[int] = mapped_column(INTEGER(11))
    mark: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text('0'))


class OcMemoriesPlanet(Base):
    __tablename__ = 'oc_memories_planet'
    __table_args__ = (
        Index('memories_planet_osm_id_index', 'osm_id'),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    osm_id: Mapped[int] = mapped_column(INTEGER(11))
    name: Mapped[str] = mapped_column(LONGTEXT)
    admin_level: Mapped[int] = mapped_column(INTEGER(11))
    other_names: Mapped[Optional[str]] = mapped_column(LONGTEXT)


class OcPhotosAlbums(Base):
    __tablename__ = 'oc_photos_albums'
    __table_args__ = (
        Index('pa_user', 'user'),
    )

    album_id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    user: Mapped[str] = mapped_column(String(255))
    created: Mapped[int] = mapped_column(BIGINT(20))
    location: Mapped[str] = mapped_column(String(255))
    last_added_photo: Mapped[int] = mapped_column(BIGINT(20))


class OcPhotosAlbumsCollabs(Base):
    __tablename__ = 'oc_photos_albums_collabs'
    __table_args__ = (
        Index('album_collabs_uniq_collab', 'album_id', 'collaborator_id', 'collaborator_type', unique=True),
    )

    id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True)
    album_id: Mapped[int] = mapped_column(BIGINT(20))
    collaborator_id: Mapped[str] = mapped_column(String(64))
    collaborator_type: Mapped[int] = mapped_column(INTEGER(11))


class OcPhotosAlbumsFiles(Base):
    __tablename__ = 'oc_photos_albums_files'
    __table_args__ = (
        Index('paf_album_file', 'album_id', 'file_id', unique=True),
        Index('paf_folder', 'album_id')
    )

    album_file_id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True, autoincrement=True)
    album_id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True)
    file_id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True)
    added: Mapped[int] = mapped_column(BIGINT(20))
    owner: Mapped[Optional[str]] = mapped_column(String(64))



class OcRecognizeFaceClusters(Base):
    __tablename__ = 'oc_recognize_face_clusters'
    __table_args__ = (
        Index('recognize_faceclust_user', 'user_id'),
    )

    id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True)
    title: Mapped[str] = mapped_column(String(4000), server_default=text("''"))
    user_id: Mapped[str] = mapped_column(String(64), server_default=text("''"))


class OcRecognizeFaceDetections(Base):
    __tablename__ = 'oc_recognize_face_detections'
    __table_args__ = (
        Index('recognize_facedet_cluster', 'cluster_id'),
        Index('recognize_facedet_file', 'file_id'),
        Index('recognize_facedet_user', 'user_id')
    )

    id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True)
    vector: Mapped[str] = mapped_column(LONGTEXT)
    threshold: Mapped[decimal.Decimal] = mapped_column(Double(asdecimal=True), server_default=text('0'))
    user_id: Mapped[Optional[str]] = mapped_column(String(64))
    file_id: Mapped[Optional[int]] = mapped_column(BIGINT(20))
    x: Mapped[Optional[decimal.Decimal]] = mapped_column(Double(asdecimal=True))
    y: Mapped[Optional[decimal.Decimal]] = mapped_column(Double(asdecimal=True))
    height: Mapped[Optional[decimal.Decimal]] = mapped_column(Double(asdecimal=True))
    width: Mapped[Optional[decimal.Decimal]] = mapped_column(Double(asdecimal=True))
    cluster_id: Mapped[Optional[int]] = mapped_column(BIGINT(20))


class OcRecognizeQueueFaces(Base):
    __tablename__ = 'oc_recognize_queue_faces'
    __table_args__ = (
        Index('recognize_faces_file', 'file_id'),
        Index('recognize_faces_storage', 'storage_id', 'root_id')
    )

    id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True)
    file_id: Mapped[int] = mapped_column(BIGINT(20))
    storage_id: Mapped[Optional[int]] = mapped_column(BIGINT(20))
    root_id: Mapped[Optional[int]] = mapped_column(BIGINT(20))
    update: Mapped[Optional[int]] = mapped_column(TINYINT(1))


class OcRecognizeQueueImagenet(Base):
    __tablename__ = 'oc_recognize_queue_imagenet'
    __table_args__ = (
        Index('recognize_imagenet_file', 'file_id'),
        Index('recognize_imagenet_storage', 'storage_id', 'root_id')
    )

    id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True)
    file_id: Mapped[int] = mapped_column(BIGINT(20))
    storage_id: Mapped[Optional[int]] = mapped_column(BIGINT(20))
    root_id: Mapped[Optional[int]] = mapped_column(BIGINT(20))
    update: Mapped[Optional[int]] = mapped_column(TINYINT(1))


class OcRecognizeQueueLandmarks(Base):
    __tablename__ = 'oc_recognize_queue_landmarks'
    __table_args__ = (
        Index('recognize_landmarks_file', 'file_id'),
        Index('recognize_landmarks_storage', 'storage_id', 'root_id')
    )

    id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True)
    file_id: Mapped[int] = mapped_column(BIGINT(20))
    storage_id: Mapped[Optional[int]] = mapped_column(BIGINT(20))
    root_id: Mapped[Optional[int]] = mapped_column(BIGINT(20))
    update: Mapped[Optional[int]] = mapped_column(TINYINT(1))


class OcRecognizeQueueMovinet(Base):
    __tablename__ = 'oc_recognize_queue_movinet'
    __table_args__ = (
        Index('recognize_movinet_file', 'file_id'),
        Index('recognize_movinet_storage', 'storage_id', 'root_id')
    )

    id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True)
    file_id: Mapped[int] = mapped_column(BIGINT(20))
    storage_id: Mapped[Optional[int]] = mapped_column(BIGINT(20))
    root_id: Mapped[Optional[int]] = mapped_column(BIGINT(20))
    update: Mapped[Optional[int]] = mapped_column(TINYINT(1))


class OcRecognizeQueueMusicnn(Base):
    __tablename__ = 'oc_recognize_queue_musicnn'
    __table_args__ = (
        Index('recognize_musicnn_file', 'file_id'),
        Index('recognize_musicnn_storage', 'storage_id', 'root_id')
    )

    id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True)
    file_id: Mapped[int] = mapped_column(BIGINT(20))
    storage_id: Mapped[Optional[int]] = mapped_column(BIGINT(20))
    root_id: Mapped[Optional[int]] = mapped_column(BIGINT(20))
    update: Mapped[Optional[int]] = mapped_column(TINYINT(1))



class OcStorages(Base):
    __tablename__ = 'oc_storages'
    __table_args__ = (
        Index('storages_id_index', 'id', unique=True),
    )

    numeric_id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True)
    available: Mapped[int] = mapped_column(INTEGER(11), server_default=text('1'))
    id: Mapped[Optional[str]] = mapped_column(String(64))
    last_checked: Mapped[Optional[int]] = mapped_column(INTEGER(11))


class OcStoragesCredentials(Base):
    __tablename__ = 'oc_storages_credentials'
    __table_args__ = (
        Index('stocred_ui', 'user', 'identifier', unique=True),
        Index('stocred_user', 'user')
    )

    id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True)
    identifier: Mapped[str] = mapped_column(String(64))
    user: Mapped[Optional[str]] = mapped_column(String(64))
    credentials: Mapped[Optional[str]] = mapped_column(LONGTEXT)

class OcSystemtag(Base):
    __tablename__ = 'oc_systemtag'
    __table_args__ = (
        Index('tag_ident', 'name', 'visibility', 'editable', unique=True),
    )

    id: Mapped[int] = mapped_column(BIGINT(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(64), server_default=text("''"))
    visibility: Mapped[int] = mapped_column(SMALLINT(6), server_default=text('1'))
    editable: Mapped[int] = mapped_column(SMALLINT(6), server_default=text('1'))


class OcSystemtagGroup(Base):
    __tablename__ = 'oc_systemtag_group'

    systemtagid: Mapped[int] = mapped_column(BIGINT(20), primary_key=True, server_default=text('0'))
    gid: Mapped[str] = mapped_column(String(255), primary_key=True)


class OcSystemtagObjectMapping(Base):
    __tablename__ = 'oc_systemtag_object_mapping'
    __table_args__ = (
        Index('memories_type_tagid', 'objecttype', 'systemtagid'),
        Index('systag_by_objectid', 'objectid'),
        Index('systag_by_tagid', 'systemtagid', 'objecttype')
    )

    objectid: Mapped[str] = mapped_column(String(64), primary_key=True, server_default=text("''"))
    objecttype: Mapped[str] = mapped_column(String(64), primary_key=True, server_default=text("''"))
    systemtagid: Mapped[int] = mapped_column(BIGINT(20), primary_key=True, server_default=text('0'))



class OcUsers(Base):
    __tablename__ = 'oc_users'
    __table_args__ = (
        Index('user_uid_lower', 'uid_lower'),
    )

    uid: Mapped[str] = mapped_column(String(64), primary_key=True, server_default=text("''"))
    password: Mapped[str] = mapped_column(String(255), server_default=text("''"))
    displayname: Mapped[Optional[str]] = mapped_column(String(64))
    uid_lower: Mapped[Optional[str]] = mapped_column(String(64), server_default=text("''"))


class OcUsersExternal(Base):
    __tablename__ = 'oc_users_external'

    backend: Mapped[str] = mapped_column(String(128), primary_key=True, server_default=text("''"))
    uid: Mapped[str] = mapped_column(String(64), primary_key=True, server_default=text("''"))
    displayname: Mapped[Optional[str]] = mapped_column(String(64))

