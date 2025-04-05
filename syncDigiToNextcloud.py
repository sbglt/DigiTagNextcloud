from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from syncFaces import syncFaces

NEXTCLOUD_USER = 'NEXTCLOUD_USER'
NEXTCLOUD_ROOTPATH = 'NEXTCLOUD_ROOT_PATH'
NEXTCLOUD_RECOGNIZE_MODEL = 1

# Connexion à Nextcloud (MySQL)
NEXTCLOUD_DATABASE_URL = "mysql+pymysql://DATABASE_CREDENTIALS"
nc_engine = create_engine(NEXTCLOUD_DATABASE_URL, echo=True)

# Création d'une session Nextcloud
NC_Session = sessionmaker(bind=nc_engine)
nc_session = NC_Session()

# Connexion à DIGIKAM (sqlite)
DIGIKAM_DATABASE_URL = "sqlite:////Users/DIGIKAM_SQLITE"
dgk_engine = create_engine(DIGIKAM_DATABASE_URL, echo=True)

# Création d'une session Digikam
DGK_Session = sessionmaker(bind=dgk_engine)
dgk_session = DGK_Session()


syncFaces(NEXTCLOUD_USER, NEXTCLOUD_ROOTPATH, NEXTCLOUD_RECOGNIZE_MODEL, nc_session, dgk_session)


nc_session.close()
dgk_session.close()
