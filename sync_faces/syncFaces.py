import json
import time
from datetime import datetime
import xml.etree.ElementTree as ET

from sqlalchemy.orm import aliased

from models.digikam4_model import Tags, ImageTagProperties, Images, Albums
from face import Rect
from models.nextcloud_model import OcFacerecogPersons, OcFacerecogFaces, OcFilecache, OcFacerecogImages

BATCH_SIZE = 1000


def create_all_facerecog_persons(NEXTCLOUD_USER, nc_session, dgk_session):
    debut = time.time()
    now = datetime.now()

    # Charger toutes les personnes existantes en mémoire
    oc_facerecog_persons_dict = {p.name: p for p in
                                 nc_session.query(OcFacerecogPersons).filter(OcFacerecogPersons.user == NEXTCLOUD_USER)}

    # Lister les Tags dont Tags.pid=4 (person)
    TagsPeople = aliased(Tags)
    dgk_tags = (
        dgk_session.query(Tags)
        .join(TagsPeople, Tags.pid == TagsPeople.id)
        .filter(TagsPeople.name == 'People')
        .filter(~Tags.name.in_(['Unknown', 'Ignored', 'Unconfirmed']))
    )

    for dgk_tag in dgk_tags:
        if oc_facerecog_persons_dict.get(dgk_tag.name) is None:
            oc_facerecog_person_new = OcFacerecogPersons(name=dgk_tag.name,
                                                         last_generation_time=now.strftime("%Y-%m-%d %H:%M:%S"),
                                                         user=NEXTCLOUD_USER)
            nc_session.add(oc_facerecog_person_new)
    nc_session.commit()

    print(f"createAllFacerecogPersons : {time.time() - debut:.2f} secondes")


def create_all_facerecog_images(NEXTCLOUD_USER, NEXTCLOUD_ROOTPATH, NEXTCLOUD_RECOGNIZE_MODEL, NEXTCLOUD_STORAGE,
                                nc_session, dgk_session):
    debut = time.time()
    now = datetime.now()
    compteur = 0

    # Lister les ImagesTagProperties
    imagesTagProperties = (dgk_session.query(ImageTagProperties, Images.id, Images.name, Albums.relativePath)
                           .filter(ImageTagProperties.property == 'tagRegion')
                           .join(Images, Images.id == ImageTagProperties.imageid)
                           .join(Albums, Albums.id == Images.album))

    # Lister les oc_facerecog_images et créer un dictionnaire par pathname
    results = (nc_session.query(OcFacerecogImages, OcFilecache)
               .filter(OcFacerecogImages.user == NEXTCLOUD_USER)
               .join(OcFilecache, OcFilecache.fileid == OcFacerecogImages.file)
               .all())
    oc_facerecog_images_bypath_dict = {filecache.path: image for image, filecache in results}

    # Lister tous les oc_filecache
    oc_filecache_dict = {p.path: p for p in
                         nc_session.query(OcFilecache).filter(OcFilecache.storage == NEXTCLOUD_STORAGE)}

    for imageTagProperties, image_id, image_name, album_path in imagesTagProperties:
        oc_facerecog_image = oc_facerecog_images_bypath_dict.get(NEXTCLOUD_ROOTPATH + album_path + '/' + image_name)
        if oc_facerecog_image is None:
            # Chercher le oc_filecache
            oc_filecache = oc_filecache_dict.get(NEXTCLOUD_ROOTPATH + album_path + '/' + image_name)
            if oc_filecache is not None:
                oc_facerecog_image = OcFacerecogImages(user=NEXTCLOUD_USER,
                                                       file=oc_filecache.fileid,
                                                       model=NEXTCLOUD_RECOGNIZE_MODEL,
                                                       is_processed=1,
                                                       last_processed_time=now.strftime(
                                                           "%Y-%m-%d %H:%M:%S"))
                nc_session.add(oc_facerecog_image)
                compteur += 1

                if compteur % BATCH_SIZE == 0:
                    try:
                        nc_session.commit()
                    except Exception as e:
                        nc_session.rollback()
                        print(f"Erreur pendant commit batch : {e}")
            else:
                print("Image non trouvée sur NEXTCLOUD : " + album_path + '/' + image_name)

    try:
        nc_session.commit()
    except Exception as e:
        nc_session.rollback()
        print(f"Erreur pendant commit final : {e}")

    print(f"createAllFacerecogImages : {time.time() - debut:.2f} secondes")


def sync_faces(NEXTCLOUD_USER, NEXTCLOUD_ROOTPATH, NEXTCLOUD_RECOGNIZE_MODEL, nc_session, dgk_session):
    debut = time.time()
    compteur = 0

    # Charger toutes les personnes existantes en mémoire
    oc_facerecog_persons_dict = {p.name: p for p in
                                 nc_session.query(OcFacerecogPersons).filter(OcFacerecogPersons.user == NEXTCLOUD_USER)}

    # Lister les oc_facerecog_images
    results = (nc_session.query(OcFacerecogImages, OcFilecache)
               .filter(OcFacerecogImages.user == NEXTCLOUD_USER)
               .join(OcFilecache, OcFilecache.fileid == OcFacerecogImages.file)
               .all())
    oc_facerecog_images_bypath_dict = {filecache.path: image for image, filecache in results}

    # Lister tous les oc_facerecog_faces et créer une clé avec oc_facerecog_images.id et oc_facerecog_persons.id
    oc_facerecog_faces_by_image_person_dict = {str(p.image) + "-" + str(p.person): p for p in
                                               nc_session.query(OcFacerecogFaces)
                                               .join(OcFacerecogImages, OcFacerecogImages.id == OcFacerecogFaces.image)
                                               .filter(OcFacerecogImages.user == NEXTCLOUD_USER)}

    now = datetime.now()

    # Traiter les Tags dont Tags.pid=4 (person) ordonné par Tags.id
    TagsPeople = aliased(Tags)
    dgk_tags = (
        dgk_session.query(Tags)
        .join(TagsPeople, Tags.pid == TagsPeople.id)
        .filter(TagsPeople.name == 'People')
        .filter(~Tags.name.in_(['Unknown', 'Ignored', 'Unconfirmed']))
    )

    for dgk_tag in dgk_tags:
        print("Personne en cours : " + dgk_tag.name)

        # Chercher la première oc_facerecog_persons avec oc_facerecog_persons.name = Tags.name
        oc_facerecog_person = oc_facerecog_persons_dict.get(dgk_tag.name)

        # Lister les oc_facerecog_faces dont oc_facerecog_faces.person = oc_facerecog_persons.id
        # oc_facerecog_faces_to_delete = list(nc_session.query(OcFacerecogFaces)
        #                                    .filter(OcFacerecogFaces.person == oc_facerecog_person.id))

        # Traiter les ImagesTagProperties avec ImagesTagProperties.tagid = Tags.id
        imagesTagProperties = (dgk_session.query(ImageTagProperties, Images.id, Images.name, Albums.relativePath)
                               .filter(ImageTagProperties.tagid == dgk_tag.id)
                               .filter(ImageTagProperties.property == 'tagRegion')
                               .join(Images, Images.id == ImageTagProperties.imageid)
                               .join(Albums, Albums.id == Images.album)
                               )

        for ImagesTagProperty, image_id, image_name, album_path in imagesTagProperties:

            oc_facerecog_image = (
                oc_facerecog_images_bypath_dict.get(NEXTCLOUD_ROOTPATH + album_path + '/' + image_name))

            # Zone correspondant au tag digikam
            dgk_face = Rect.from_xml(ET.fromstring(ImagesTagProperty.value))

            if oc_facerecog_image is not None:
                # Est-ce que l'image comporte un tag pour cette personne
                oc_facerecog_face = oc_facerecog_faces_by_image_person_dict.get(
                    str(oc_facerecog_image.id) + "-" + str(oc_facerecog_person.id))

                create_new_oc_facerecog_face = True
                if oc_facerecog_face is not None:
                    # Comparer la zone avec celle de ImagesTagProperties
                    nc_face = Rect(oc_facerecog_face.x, oc_facerecog_face.y, oc_facerecog_face.width,
                                   oc_facerecog_face.height)

                    # Si la zone est différente
                    if not nc_face.is_close(dgk_face, tolerance=0.2):
                        # Supprimer le oc_facerecog_faces
                        print("TODO")
                        nc_session.delete(oc_facerecog_face)

                    else:
                        # Retirer oc_facerecog_faces.id de la liste des oc_facerecog_faces non traités
                        create_new_oc_facerecog_face = False
                        oc_facerecog_faces_by_image_person_dict.pop(
                            str(oc_facerecog_face.image) + "-" + str(oc_facerecog_face.person))

                # Si aucun oc_facerecog_faces, créer un couple oc_facerecog_faces et oc_facerecog_images
                if create_new_oc_facerecog_face:
                    # Créer un nouveau oc_facerecog_faces pour oc_facerecog_person
                    oc_facerecog_face_new = OcFacerecogFaces(image=oc_facerecog_image.id,
                                                             confidence=1.01,
                                                             creation_time=now.strftime("%Y-%m-%d %H:%M:%S"),
                                                             landmarks=json.dumps({
                                                                 "source": "digikam"
                                                             }),
                                                             descriptor=json.dumps({
                                                                 "source": "digikam"
                                                             }),
                                                             x=dgk_face.x,
                                                             y=dgk_face.y,
                                                             width=dgk_face.width,
                                                             height=dgk_face.height,
                                                             person=oc_facerecog_person.id)
                    nc_session.add(oc_facerecog_face_new)
                    compteur += 1

                    if compteur % BATCH_SIZE == 0:
                        try:
                            nc_session.commit()
                        except Exception as e:
                            nc_session.rollback()
                            print(f"Erreur pendant commit batch : {e}")
            else:
                print("Pas de oc_facerecog_image !!!")

        # Retirer la personne de la liste des personnes à traiter
        oc_facerecog_persons_dict.pop(oc_facerecog_person.name)

    # Parcourir les oc_facerecog_faces existants non traités
    for f in oc_facerecog_faces_by_image_person_dict:
        print("Suppression face : " + str(oc_facerecog_faces_by_image_person_dict[f].id))
        nc_session.delete(oc_facerecog_faces_by_image_person_dict[f])
        compteur += 1

        if compteur % BATCH_SIZE == 0:
            try:
                nc_session.commit()
            except Exception as e:
                nc_session.rollback()
                print(f"Erreur pendant commit batch : {e}")

    # Parcourir les oc_facerecog_persons non traités
    for p in oc_facerecog_persons_dict:
        print("Suppression person : " + p.name)
        nc_session.delete(oc_facerecog_persons_dict[p])
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

    print(f"sync_faces :  {time.time() - debut:.2f} secondes")
    print("sync_faces : Terminé")
