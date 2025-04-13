import json
import time
from datetime import datetime
import xml.etree.ElementTree as ET

from sqlalchemy.orm import aliased

from digikam4_model import Tags, ImageTags, Images, Albums
from nextcloud_model import OcPhotosAlbums, OcFilecache, OcPhotosAlbumsFiles

BATCH_SIZE = 1000


def create_all_oc_photos_albums(NEXTCLOUD_USER, NEXTCLOUD_ROOTPATH, NEXTCLOUD_STORAGE, nc_session, dgk_session):
    debut = time.time()
    now = datetime.now()
    compteur = 0

    # Lister les Albums à synchroniser depuis Digikam (Tags dont Tags.inconkde contient 'nextcloud.png')
    dgk_tags = (
        dgk_session.query(Tags)
        .filter(Tags.iconkde.ilike('%nextcloud.png'))
    )

    # ETAPE 1 : Créer les oc_photos_albums manquants
    # Charger tous les albums Nextcloud en mémoire
    oc_photos_albums_dict = {p.name: p for p in
                             nc_session.query(OcPhotosAlbums).filter(OcPhotosAlbums.user == NEXTCLOUD_USER)}

    # Parcourir les albums pour créer les oc_photos_albums
    for dgk_tag in dgk_tags:
        if oc_photos_albums_dict.get(dgk_tag.name) is None:
            oc_photos_albums_new = OcPhotosAlbums(name=dgk_tag.name,
                                                  location="",
                                                  created=now.timestamp(),
                                                  last_added_photo=-1,
                                                  user=NEXTCLOUD_USER)
            nc_session.add(oc_photos_albums_new)
    nc_session.commit()

    # ETAPE 2 : Synchroniser les oc_photos_albums_files
    # Re-charger tous les albums Nextcloud en mémoire
    oc_photos_albums_dict = {p.name: p for p in
                             nc_session.query(OcPhotosAlbums).filter(OcPhotosAlbums.user == NEXTCLOUD_USER)}

    # Lister tous les oc_filecache
    oc_filecache_dict = {p.path: p for p in
                         nc_session.query(OcFilecache).filter(OcFilecache.storage == NEXTCLOUD_STORAGE)}



    # Parcourir les Albums digikam
    for dgk_tag in dgk_tags:
        # Lister les ImagesTag
        images_tags = (dgk_session.query(ImageTags, Images.id, Images.name, Albums.relativePath)
                       .filter(ImageTags.tagid == dgk_tag.id)
                       .join(Images, Images.id == ImageTags.imageid)
                       .join(Albums, Albums.id == Images.album))

        oc_photos_albums = oc_photos_albums_dict.get(dgk_tag.name)

        # Lister tous les oc_photos_albums_files avec une clé Album.name-ImageFullPathName
        oc_photos_albums_files_dict = {photo_album.name + "-" + filecache.path: photo_album_file
                                       for photo_album_file, photo_album, filecache in
                                       nc_session.query(OcPhotosAlbumsFiles, OcPhotosAlbums,
                                                        OcFilecache)
                                       .filter(OcPhotosAlbumsFiles.owner == NEXTCLOUD_USER)
                                       .filter(OcPhotosAlbums.name == dgk_tag.name)
                                       .join(OcPhotosAlbums, OcPhotosAlbums.album_id == OcPhotosAlbumsFiles.album_id)
                                       .join(OcFilecache, OcFilecache.fileid == OcPhotosAlbumsFiles.file_id)}

        image_ajoutee = False
        for image_tags, image_id, image_name, album_path in images_tags:

            oc_photo_album_file = oc_photos_albums_files_dict.get(
                dgk_tag.name + '-' + NEXTCLOUD_ROOTPATH + album_path + '/' + image_name)
            if oc_photo_album_file is None:
                # Chercher le oc_filecache
                oc_filecache = oc_filecache_dict.get(NEXTCLOUD_ROOTPATH + album_path + '/' + image_name)
                if oc_filecache is not None:
                    oc_photo_album_file = OcPhotosAlbumsFiles(file_id=oc_filecache.fileid,
                                                              album_id=oc_photos_albums.album_id,
                                                              owner=NEXTCLOUD_USER,
                                                              added=now.timestamp())
                    nc_session.add(oc_photo_album_file)
                    compteur += 1
                    image_ajoutee = True

                    if compteur % BATCH_SIZE == 0:
                        try:
                            nc_session.commit()
                        except Exception as e:
                            nc_session.rollback()
                            print(f"Erreur pendant commit batch : {e}")
                else:
                    print("Image non trouvée sur NEXTCLOUD : " + album_path + '/' + image_name)
            else:
                oc_photos_albums_files_dict.pop(dgk_tag.name + '-' + NEXTCLOUD_ROOTPATH + album_path + '/' + image_name)

        if image_ajoutee:
            oc_photos_albums.last_added_photo = now.toordinal() + 1721425
            compteur += 1
            if compteur % BATCH_SIZE == 0:
                try:
                    nc_session.commit()
                except Exception as e:
                    nc_session.rollback()
                    print(f"Erreur pendant commit batch : {e}")

        # Supprimer les photos en trop dans les albums
        for f in oc_photos_albums_files_dict:
            print("Retrait photo de l'album : album : " + str(
                oc_photos_albums_files_dict[f].album_id) + ", photo : " + str(
                oc_photos_albums_files_dict[f].file_id))
            nc_session.delete(oc_photos_albums_files_dict[f])
            compteur += 1

            if compteur % BATCH_SIZE == 0:
                try:
                    nc_session.commit()
                except Exception as e:
                    nc_session.rollback()
                    print(f"Erreur pendant commit batch : {e}")

    try:
        nc_session.commit()
    except Exception as e:
        nc_session.rollback()
        print(f"Erreur pendant commit final : {e}")

    print(f"create_all_oc_photos_albums : {time.time() - debut:.2f} secondes")
