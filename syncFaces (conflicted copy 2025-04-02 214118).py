import json
from datetime import datetime
import xml.etree.ElementTree as ET

from sqlalchemy.orm import aliased

from digikam4_model import Tags, ImageTagProperties, Images, Albums
from face import Rect
from nextcloud_model import OcFacerecogPersons, OcFacerecogFaces, OcFilecache, OcFacerecogImages


def syncFaces(NEXTCLOUD_USER, NEXTCLOUD_ROOTPATH, nc_session, dgk_session):
    # Lister les oc_facerecog_persons
    oc_facerecog_persons_to_delete = list(nc_session.query(OcFacerecogPersons))

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
            oc_facerecog_person_new = OcFacerecogPersons(name=dgk_tag.name, last_generation_time=datetime.now,
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
        ImagesTagProperties = dgk_session.query(ImageTagProperties).filter(ImageTagProperties.tagid == dgk_tag.id)
        for ImagesTagProperty in ImagesTagProperties:

            now = datetime.now()
            # Identifier le fichier DIGIKAM sans le volume
            # fullPathName = Album.relativePath + "/" + Images.name  (ex : /2023/2023-08-05 + "/" + IMG_5309.JPG)
            dgk_image = dgk_session.query(Images).filter(Images.id == ImagesTagProperty.imageid).one_or_none()
            if dgk_image is not None:
                dgk_album = dgk_session.query(Albums).filter(Albums.id == dgk_image.album).one_or_none()
                if dgk_album is None:
                    print('probleme')
                dgk_image_fullpath = dgk_album.relativePath + '/' + dgk_image.name
                print(dgk_image_fullpath)

                if dgk_image_fullpath == '/2018-02-10/IMG_3191.JPG':

                    # Chercher le fichier Nextcloud oc_filecache correspondant au fichier :
                    # oc_filecache.path = fullPathName (sans files/PhotosFamille...l'ajouter ou faire un 'like %' ?)
                    oc_filecache_image = (nc_session.query(OcFilecache)
                                          .filter(OcFilecache.path == NEXTCLOUD_ROOTPATH + dgk_image_fullpath).first())

                    dgk_face = Rect.from_xml(ET.fromstring(ImagesTagProperty.value))

                    # Si oc_facerecog_persons existait déjà
                    if oc_facerecog_person:
                        # Est-ce que l'image comporte un tag pour cette personne ? =
                        # Chercher les oc_facerecog_images pointant le fichier oc_filecache :
                        # oc_facerecog_images.file = oc_filecache.fileid
                        # et pointant un oc_facerecog_faces oc_facerecog_images.id = oc_facerecog_faces.image
                        # avec oc_facerecog_faces.person = oc_facerecog_persons.id
                        oc_facerecog_faces = (nc_session.query(OcFacerecogFaces)
                                              .join(OcFacerecogPersons, OcFacerecogPersons.id == oc_facerecog_person.id)
                                              .join(OcFacerecogImages, OcFacerecogFaces.image == OcFacerecogImages.id)
                                              .filter(OcFacerecogImages.user == NEXTCLOUD_USER)
                                              .filter(OcFacerecogImages.file == oc_filecache_image.fileid)
                                              )
                        create_new_oc_facerecog_face = True
                        for oc_facerecog_face in oc_facerecog_faces:
                            # Comparer la zone avec celle de ImagesTagProperties
                            nc_face = Rect(oc_facerecog_face.x, oc_facerecog_face.y, oc_facerecog_face.width,
                                           oc_facerecog_face.height)

                            # Si la zone est différente
                            if not nc_face.is_close(dgk_face, tolerance=0.2):
                                # Supprimer le oc_facerecog_faces et oc_facerecog_images
                                oc_facerecog_image = (nc_session.query(OcFacerecogImages)
                                                      .filter(OcFacerecogImages.user == NEXTCLOUD_USER)
                                                      .filter(OcFacerecogImages.file == oc_filecache_image.fileid)
                                                      .filter(OcFacerecogImages.id == oc_facerecog_face.image)
                                                      )
                                #nc_session.delete(oc_facerecog_image)
                                #nc_session.delete(oc_facerecog_face)
                                #nc_session.commit()

                            else:
                                # Retirer oc_facerecog_faces.id de la liste des oc_facerecog_faces non traités
                                create_new_oc_facerecog_face = False
                                for i, p in enumerate(oc_facerecog_faces_to_delete):
                                    if p.id == oc_facerecog_face.id:
                                        oc_facerecog_faces_to_delete.pop(i)

                        # Si aucun oc_facerecog_faces, créer un couple oc_facerecog_faces et oc_facerecog_images
                        if create_new_oc_facerecog_face:
                            # Créer un nouveau oc_facerecog_images pour oc_facerecog_person
                            # Créer un nouveau oc_facerecog_faces pour oc_facerecog_person
                            oc_facerecog_image_new = OcFacerecogImages(user=NEXTCLOUD_USER,
                                                                       file=oc_filecache_image.fileid,
                                                                       model=1,
                                                                       is_processed=1,
                                                                       last_processed_time=now.strftime("%Y-%m-%d %H:%M:%S"))
                            nc_session.add(oc_facerecog_image_new)
                            nc_session.flush()
                            oc_facerecog_face_new = OcFacerecogFaces(image=oc_facerecog_image_new.id,
                                                                     confidence=1.01,
                                                                     creation_time=now.strftime("%Y-%m-%d %H:%M:%S"),
                                                                     landmarks=json.dumps([{"x":1,"y":1},{"x":1,"y":1},{"x":1,"y":1},{"x":1,"y":1},{"x":1,"y":1}]),
                                                                     descriptor=json.dumps([-0.08316531032323837,0.13774508237838745,0.03313063830137253,-0.02593918889760971,-0.1160786971449852,-0.022883713245391846,-0.03691551834344864,-0.03463608771562576,0.09251680225133896,-0.04452700912952423,0.16168422996997833,-0.10205084085464478,-0.27976852655410767,-0.01793215423822403,-0.0007751472294330597,0.1203463226556778,-0.14078454673290253,-0.1083180159330368,-0.23557698726654053,-0.1592511087656021,-0.03474058955907822,0.022762728855013847,-0.017331266775727272,-0.04558824002742767,-0.16930457949638367,-0.28048932552337646,-0.07388230413198471,-0.10277368873357773,0.0693015605211258,-0.13435766100883484,0.05786328762769699,0.0442652702331543,-0.16749581694602966,-0.05448755621910095,0.009127873927354813,-0.017013296484947205,-0.03280629217624664,-0.020382754504680634,0.1958305686712265,0.014957902953028679,-0.18444907665252686,0.047108858823776245,0.050683993846178055,0.2876693606376648,0.20928877592086792,0.0071660056710243225,-0.016956590116024017,-0.046681735664606094,0.06191109120845795,-0.2715625464916229,-0.0055181607604026794,0.2143673598766327,0.08134374022483826,0.13259994983673096,0.06877747923135757,-0.06227939575910568,0.05421922355890274,0.17638881504535675,-0.20683653652668,0.05878433212637901,0.08490254729986191,-0.09719699621200562,-0.09533055871725082,-0.04934440553188324,0.18994322419166565,0.10344492644071579,-0.08273596316576004,-0.16614001989364624,0.20581567287445068,-0.14540328085422516,-0.05015726760029793,0.11509107798337936,-0.09484075009822845,-0.14066943526268005,-0.2758137285709381,0.057271964848041534,0.4048386812210083,0.17834150791168213,-0.18468013405799866,-0.016106337308883667,-0.11922721564769745,-0.044663526117801666,0.017404381185770035,0.0023489054292440414,-0.13203154504299164,-0.0814107283949852,-0.03495866805315018,0.08629827946424484,0.1998652219772339,-0.040123552083969116,-0.008576810359954834,0.1954418420791626,0.07688586413860321,-0.03256281465291977,-0.0036012083292007446,0.005321010947227478,-0.10741867125034332,-0.10066982358694077,-0.11044716089963913,-0.0628003403544426,0.10554023832082748,-0.1159445196390152,0.009575463831424713,0.13840363919734955,-0.15843582153320312,0.22455282509326935,0.02292107231914997,-0.05035331845283508,-0.02354898303747177,0.05176550894975662,0.03539004921913147,0.006907898932695389,0.2163650244474411,-0.21746161580085754,0.2097335159778595,0.22807639837265015,0.020860373973846436,0.03987952321767807,0.03728608787059784,0.045095764100551605,-0.048724424093961716,0.00621766597032547,-0.1450517177581787,-0.12599676847457886,0.00493796169757843,-0.03476884961128235,-0.007696382701396942,0.030325844883918762]),
                                                                     x=dgk_face.x,
                                                                     y=dgk_face.y,
                                                                     width=dgk_face.width,
                                                                     height=dgk_face.height,
                                                                     person=oc_facerecog_person.id)
                            nc_session.add(oc_facerecog_face_new)
                            nc_session.commit()

                        # Supprimer les oc_facerecog_faces (et oc_facerecog_images) faisant partie de la liste des non traités
                        #for i, p in enumerate(oc_facerecog_faces_to_delete):
                            # oc_facerecog_image_to_delete = (nc_session.query(OcFacerecogImages)
                            #                                .filter(OcFacerecogImages.id == p.image)).one_or_none()
                            #nc_session.delete(oc_facerecog_image_to_delete, p)
                    else:
                        # Créer un nouveau oc_facerecog_images pour oc_facerecog_person_new
                        # Créer un nouveau oc_facerecog_faces pour oc_facerecog_person_new
                        oc_facerecog_image_new = OcFacerecogImages(user=NEXTCLOUD_USER,
                                                                   file=oc_filecache_image.fileid,
                                                                   model=1,
                                                                   is_processed=1)
                        nc_session.add(oc_facerecog_image_new)
                        nc_session.flush()
                        oc_facerecog_face_new = OcFacerecogFaces(image=oc_facerecog_image_new.id,
                                                                 confidence=1,
                                                                 creation_time=now.strftime("%Y-%m-%d %H:%M:%S"),
                                                                 landmarks=json.dumps(
                                                                     [{"x": 1, "y": 1}, {"x": 1, "y": 1}, {"x": 1, "y": 1},
                                                                      {"x": 1, "y": 1}, {"x": 1, "y": 1}]),
                                                                 descriptor=json.dumps(
                                                                     [-0.08316531032323837, 0.13774508237838745,
                                                                      0.03313063830137253, -0.02593918889760971,
                                                                      -0.1160786971449852, -0.022883713245391846,
                                                                      -0.03691551834344864, -0.03463608771562576,
                                                                      0.09251680225133896, -0.04452700912952423,
                                                                      0.16168422996997833, -0.10205084085464478,
                                                                      -0.27976852655410767, -0.01793215423822403,
                                                                      -0.0007751472294330597, 0.1203463226556778,
                                                                      -0.14078454673290253, -0.1083180159330368,
                                                                      -0.23557698726654053, -0.1592511087656021,
                                                                      -0.03474058955907822, 0.022762728855013847,
                                                                      -0.017331266775727272, -0.04558824002742767,
                                                                      -0.16930457949638367, -0.28048932552337646,
                                                                      -0.07388230413198471, -0.10277368873357773,
                                                                      0.0693015605211258, -0.13435766100883484,
                                                                      0.05786328762769699, 0.0442652702331543,
                                                                      -0.16749581694602966, -0.05448755621910095,
                                                                      0.009127873927354813, -0.017013296484947205,
                                                                      -0.03280629217624664, -0.020382754504680634,
                                                                      0.1958305686712265, 0.014957902953028679,
                                                                      -0.18444907665252686, 0.047108858823776245,
                                                                      0.050683993846178055, 0.2876693606376648,
                                                                      0.20928877592086792, 0.0071660056710243225,
                                                                      -0.016956590116024017, -0.046681735664606094,
                                                                      0.06191109120845795, -0.2715625464916229,
                                                                      -0.0055181607604026794, 0.2143673598766327,
                                                                      0.08134374022483826, 0.13259994983673096,
                                                                      0.06877747923135757, -0.06227939575910568,
                                                                      0.05421922355890274, 0.17638881504535675,
                                                                      -0.20683653652668, 0.05878433212637901,
                                                                      0.08490254729986191, -0.09719699621200562,
                                                                      -0.09533055871725082, -0.04934440553188324,
                                                                      0.18994322419166565, 0.10344492644071579,
                                                                      -0.08273596316576004, -0.16614001989364624,
                                                                      0.20581567287445068, -0.14540328085422516,
                                                                      -0.05015726760029793, 0.11509107798337936,
                                                                      -0.09484075009822845, -0.14066943526268005,
                                                                      -0.2758137285709381, 0.057271964848041534,
                                                                      0.4048386812210083, 0.17834150791168213,
                                                                      -0.18468013405799866, -0.016106337308883667,
                                                                      -0.11922721564769745, -0.044663526117801666,
                                                                      0.017404381185770035, 0.0023489054292440414,
                                                                      -0.13203154504299164, -0.0814107283949852,
                                                                      -0.03495866805315018, 0.08629827946424484,
                                                                      0.1998652219772339, -0.040123552083969116,
                                                                      -0.008576810359954834, 0.1954418420791626,
                                                                      0.07688586413860321, -0.03256281465291977,
                                                                      -0.0036012083292007446, 0.005321010947227478,
                                                                      -0.10741867125034332, -0.10066982358694077,
                                                                      -0.11044716089963913, -0.0628003403544426,
                                                                      0.10554023832082748, -0.1159445196390152,
                                                                      0.009575463831424713, 0.13840363919734955,
                                                                      -0.15843582153320312, 0.22455282509326935,
                                                                      0.02292107231914997, -0.05035331845283508,
                                                                      -0.02354898303747177, 0.05176550894975662,
                                                                      0.03539004921913147, 0.006907898932695389,
                                                                      0.2163650244474411, -0.21746161580085754,
                                                                      0.2097335159778595, 0.22807639837265015,
                                                                      0.020860373973846436, 0.03987952321767807,
                                                                      0.03728608787059784, 0.045095764100551605,
                                                                      -0.048724424093961716, 0.00621766597032547,
                                                                      -0.1450517177581787, -0.12599676847457886,
                                                                      0.00493796169757843, -0.03476884961128235,
                                                                      -0.007696382701396942, 0.030325844883918762]),

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
