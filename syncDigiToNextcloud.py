import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from checkDigikamFaceTags import check_person_unicity_for_digikam, check_person_unicity_for_each_image
from syncFaces import sync_faces, create_all_facerecog_persons, create_all_facerecog_images

NEXTCLOUD_USER = 'parents'
NEXTCLOUD_ROOTPATH = 'files/PhotosFamille'
NEXTCLOUD_RECOGNIZE_MODEL = 1
NEXTCLOUD_STORAGE = 9

debut = time.time()

# Connexion à Nextcloud (MySQL)
NEXTCLOUD_DATABASE_URL = "mysql+pymysql://root:10501119d7282c0@nextcloud.sglet.com/nextcloud"
nc_engine = create_engine(NEXTCLOUD_DATABASE_URL, echo=True)

# Création d'une session Nextcloud
NC_Session = sessionmaker(bind=nc_engine)
nc_session = NC_Session()

# Connexion à DIGIKAM (sqlite)
DIGIKAM_DATABASE_URL = "sqlite:////Users/sebastienglet/Pictures/digikam4.db"
dgk_engine = create_engine(DIGIKAM_DATABASE_URL, echo=True)

# Création d'une session Digikam
DGK_Session = sessionmaker(bind=dgk_engine)
dgk_session = DGK_Session()

has_person_unicity_problem = check_person_unicity_for_digikam(dgk_session)
has_image_person_unicity_problem = check_person_unicity_for_each_image(dgk_session)

if has_person_unicity_problem is False and has_image_person_unicity_problem is False:
    create_all_facerecog_persons(NEXTCLOUD_USER, nc_session, dgk_session)
    create_all_facerecog_images(NEXTCLOUD_USER, NEXTCLOUD_ROOTPATH, NEXTCLOUD_RECOGNIZE_MODEL, NEXTCLOUD_STORAGE,
                                nc_session, dgk_session)
    sync_faces(NEXTCLOUD_USER, NEXTCLOUD_ROOTPATH, NEXTCLOUD_RECOGNIZE_MODEL, nc_session, dgk_session)
else:
    print("Synchronisation annulée à cause de problèmes d'unicité")

nc_session.close()
dgk_session.close()
print(f"Main : {time.time() - debut:.2f} secondes")
