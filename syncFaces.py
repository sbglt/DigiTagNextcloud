import json
from datetime import datetime
import xml.etree.ElementTree as ET

from sqlalchemy.orm import aliased

from digikam4_model import Tags, ImageTagProperties, Images, Albums
from face import Rect
from nextcloud_model import OcFacerecogPersons, OcFacerecogFaces, OcFilecache, OcFacerecogImages


def syncFaces(NEXTCLOUD_USER, NEXTCLOUD_ROOTPATH, NEXTCLOUD_RECOGNIZE_MODEL, nc_session, dgk_session):
    # Lister les oc_facerecog_persons
    oc_facerecog_persons_to_delete = list(nc_session.query(OcFacerecogPersons))
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

        # Chercher la première oc_facerecog_persons avec oc_facerecog_persons.name = Tags.name
        # Les autres oc_facerecog_persons correspondant au même tag seront supprimés
        # Si besoin, créer oc_facerecog_persons
        oc_facerecog_person = (nc_session.query(OcFacerecogPersons)
                               .filter(OcFacerecogPersons.name == dgk_tag.name)
                               .filter(OcFacerecogPersons.user == NEXTCLOUD_USER).first())
        if not oc_facerecog_person:
            oc_facerecog_person_new = OcFacerecogPersons(name=dgk_tag.name,
                                                         last_generation_time=now.strftime("%Y-%m-%d %H:%M:%S"),
                                                         user=NEXTCLOUD_USER)
            nc_session.add(oc_facerecog_person_new)
            nc_session.commit()

        else:
            # Retirer la personne courante des oc_facerecog_persons non traités
            for i, p in enumerate(oc_facerecog_persons_to_delete):
                if p.id == oc_facerecog_person.id:
                    temp_facerecog_person = oc_facerecog_persons_to_delete.pop(i)
                    print(f"Personne retirée : {temp_facerecog_person.id}, {temp_facerecog_person.name}")
                    break

            # Lister les oc_facerecog_faces dont oc_facerecog_faces.person = oc_facerecog_persons.id
            oc_facerecog_faces_to_delete = list(nc_session.query(OcFacerecogFaces)
                                                .filter(OcFacerecogFaces.person == oc_facerecog_person.id))

        # Traiter les ImagesTagProperties avec ImagesTagProperties.tagid = Tags.id
        imagesTagProperties = dgk_session.query(ImageTagProperties).filter(ImageTagProperties.tagid == dgk_tag.id)
        for ImagesTagProperty in imagesTagProperties:

            # Identifier le fichier DIGIKAM sans le volume
            # fullPathName = Album.relativePath + "/" + Images.name  (ex : /2023/2023-08-05 + "/" + IMG_5309.JPG)
            dgk_image = (dgk_session.query(Images)
                         .filter(Images.id == ImagesTagProperty.imageid)
                         .filter(Images.album.isnot(None))
                         .one_or_none())

            if dgk_image is not None:
                dgk_album = dgk_session.query(Albums).filter(Albums.id == dgk_image.album).one_or_none()
                if dgk_album is None:
                    print('problem')
                dgk_image_fullpath = dgk_album.relativePath + '/' + dgk_image.name
                print(dgk_image_fullpath)

                # Zone correspondant au tag digikam
                dgk_face = Rect.from_xml(ET.fromstring(ImagesTagProperty.value))

                # Chercher le fichier Nextcloud oc_filecache correspondant au fichier :
                # oc_filecache.path = fullPathName (sans files/PhotosFamille...l'ajouter ou faire un 'like %' ?)
                oc_filecache_image = (nc_session.query(OcFilecache)
                                      .filter(OcFilecache.path == NEXTCLOUD_ROOTPATH + dgk_image_fullpath)
                                      .one_or_none())

                # Chercher oc_facerecog_image correspondant et le créer le cas échéant
                oc_facerecog_image = (nc_session.query(OcFacerecogImages)
                                      .filter(OcFacerecogImages.user == NEXTCLOUD_USER)
                                      .filter(OcFacerecogImages.file == oc_filecache_image.fileid)
                                      .filter(OcFacerecogImages.model == NEXTCLOUD_RECOGNIZE_MODEL)
                                      ).one_or_none()
                if oc_facerecog_image is None:
                    oc_facerecog_image = OcFacerecogImages(user=NEXTCLOUD_USER,
                                                           file=oc_filecache_image.fileid,
                                                           model=NEXTCLOUD_RECOGNIZE_MODEL,
                                                           is_processed=1,
                                                           last_processed_time=now.strftime(
                                                               "%Y-%m-%d %H:%M:%S"))
                    nc_session.add(oc_facerecog_image)
                    nc_session.commit()

                # Si oc_facerecog_persons existait déjà
                if oc_facerecog_person:
                    # Est-ce que l'image comporte un tag pour cette personne ? =
                    # et pointant un oc_facerecog_faces oc_facerecog_images.id = oc_facerecog_faces.image
                    # avec oc_facerecog_faces.person = oc_facerecog_persons.id
                    oc_facerecog_faces = (nc_session.query(OcFacerecogFaces)
                                          .join(OcFacerecogPersons, OcFacerecogFaces.person == OcFacerecogPersons.id)
                                          .join(OcFacerecogImages, OcFacerecogFaces.image == OcFacerecogImages.id)
                                          .filter(OcFacerecogPersons.id == oc_facerecog_person.id)
                                          )

                    create_new_oc_facerecog_face = True
                    for oc_facerecog_face in oc_facerecog_faces:
                        # Comparer la zone avec celle de ImagesTagProperties
                        nc_face = Rect(oc_facerecog_face.x, oc_facerecog_face.y, oc_facerecog_face.width,
                                       oc_facerecog_face.height)

                        # Si la zone est différente
                        if not nc_face.is_close(dgk_face, tolerance=0.2):
                            # Supprimer le oc_facerecog_faces
                            print("TODO")
                            # nc_session.delete(oc_facerecog_image)
                            # nc_session.delete(oc_facerecog_face)
                            # nc_session.commit()

                        else:
                            # Retirer oc_facerecog_faces.id de la liste des oc_facerecog_faces non traités
                            create_new_oc_facerecog_face = False
                            for i, p in enumerate(oc_facerecog_faces_to_delete):
                                if p.id == oc_facerecog_face.id:
                                    oc_facerecog_faces_to_delete.pop(i)

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
                        nc_session.commit()

                    # Supprimer les oc_facerecog_faces faisant partie de la liste des non traités
                    # for i, p in enumerate(oc_facerecog_faces_to_delete):
                    # TODO
                    # nc_session.delete(oc_facerecog_image_to_delete, p)
                else:
                    # Créer un nouveau oc_facerecog_faces pour oc_facerecog_person_new
                    oc_facerecog_face_new = OcFacerecogFaces(image=oc_facerecog_image.id,
                                                             confidence=1,
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
                                                             person=oc_facerecog_person_new.id)
                    nc_session.add(oc_facerecog_face_new)



    # Parcourir les oc_facerecog_persons non traités
    #  Supprimer les oc_facerecog_faces (et oc_facerecog_images) pointant le oc_facerecog_persons non traité
    for i, p in enumerate(oc_facerecog_persons_to_delete):
        oc_facerecog_faces_to_delete = nc_session.query(OcFacerecogFaces).filter(OcFacerecogFaces.person == p.id)
        #for oc_facerecog_face_to_delete in oc_facerecog_faces_to_delete:
            #oc_facerecog_image_to_delete = (nc_session.query(OcFacerecogImages)
            #                                .filter(OcFacerecogImages.id == oc_facerecog_face_to_delete.image)).one_or_none()
            #nc_session.delete(oc_facerecog_image_to_delete, oc_facerecog_face_to_delete)

        #nc_session.delete(p)
        print(f"Personne retirée : {p.id}, {p.name}")

    print("Terminé")
