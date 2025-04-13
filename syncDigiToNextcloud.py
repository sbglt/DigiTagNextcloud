import time
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from checkDigikamFaceTags import check_person_unicity_for_digikam, check_person_unicity_for_each_image
from syncFaces import sync_faces, create_all_facerecog_persons, create_all_facerecog_images
from syncTagsAsAlbums import create_all_oc_photos_albums

from dotenv import load_dotenv  # Pour la gestion de l'environnement DEVELOPPEMENT/PROD
env_path = load_dotenv()

NEXTCLOUD_USER = os.environ.get('NEXTCLOUD_USER')
NEXTCLOUD_ROOTPATH = os.environ.get('NEXTCLOUD_ROOTPATH')
NEXTCLOUD_RECOGNIZE_MODEL = os.environ.get('NEXTCLOUD_RECOGNIZE_MODEL')
NEXTCLOUD_STORAGE = os.environ.get('NEXTCLOUD_STORAGE')

debut = time.time()

# Connexion à Nextcloud (MySQL)
NEXTCLOUD_DATABASE_URL = os.environ.get('NEXTCLOUD_DATABASE_URL')
nc_engine = create_engine(NEXTCLOUD_DATABASE_URL, echo=True)

# Création d'une session Nextcloud
NC_Session = sessionmaker(bind=nc_engine)
nc_session = NC_Session()

# Connexion à DIGIKAM (sqlite)
DIGIKAM_DATABASE_URL = os.environ.get('DIGIKAM_DATABASE_URL')
dgk_engine = create_engine(DIGIKAM_DATABASE_URL, echo=True)

# Création d'une session Digikam
DGK_Session = sessionmaker(bind=dgk_engine)
dgk_session = DGK_Session()

has_person_unicity_problem = check_person_unicity_for_digikam(dgk_session)
has_image_person_unicity_problem = check_person_unicity_for_each_image(dgk_session)

if has_person_unicity_problem is False and has_image_person_unicity_problem is False:

    create_all_oc_photos_albums(NEXTCLOUD_USER, NEXTCLOUD_ROOTPATH, NEXTCLOUD_STORAGE, nc_session, dgk_session)

    create_all_facerecog_persons(NEXTCLOUD_USER, nc_session, dgk_session)
    create_all_facerecog_images(NEXTCLOUD_USER, NEXTCLOUD_ROOTPATH, NEXTCLOUD_RECOGNIZE_MODEL, NEXTCLOUD_STORAGE,
                                nc_session, dgk_session)
    sync_faces(NEXTCLOUD_USER, NEXTCLOUD_ROOTPATH, NEXTCLOUD_RECOGNIZE_MODEL, nc_session, dgk_session)
else:
    print("Synchronisation annulée à cause de problèmes d'unicité")




nc_session.close()
dgk_session.close()
print(f"Main : {time.time() - debut:.2f} secondes")
