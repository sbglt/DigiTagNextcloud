import os
import requests
import sqlite3
import xml.etree.ElementTree as ET
from requests.auth import HTTPBasicAuth
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import sys
import locale

# SELECT Tags.id as 'tagId',Tags.name as 'tagName', AlbumRoots.specificPath, Albums.relativePath,  Images.name
# from Tags left join ImageTags
# on Tags.id=ImageTags.tagid
# inner join Images
# on ImageTags.imageid=Images.id
# inner join Albums
# on Images.album = Albums.id
# INNER join AlbumRoots
# on AlbumRoots.id = Albums.albumRoot
# where Tags.pid=4 and  Tags.id=29

# yLC9B-BARH5-5MRJ4-T5zf8-AJHbA

# Configuration Nextcloud
NEXTCLOUD_URL = 'https://nextcloud.sglet.com'
NEXTCLOUD_USER = 'parents'
NEXTCLOUD_PASSWORD = 'yLC9B-BARH5-5MRJ4-T5zf8-AJHbA'

# Chemin vers le montage NFS contenant les photos
MOUNT_PATH = '/Volumes/PhotosFamille'

# Chemin vers la base de données Digikam (SQLite)
DIGIKAM_DB_PATH = '/Users/sebastienglet/Pictures/digikam4.db'
DIGIKAM_RECOGNITION_DB_PATH = '/Users/sebastienglet/Pictures/recognition.db'

# Fonction pour obtenir les visages depuis Digikam
def get_faces_from_digikam():
    faces = []
    try:
        conn = sqlite3.connect(DIGIKAM_DB_PATH)
        cursor = conn.cursor()

        # Requête pour extraire les visages et les informations pertinentes
        cursor.execute("""
            SELECT Tags.id as 'tagId',Tags.name as 'tagName', AlbumRoots.identifier, AlbumRoots.specificPath, Albums.relativePath,  Images.name 
            from Tags left join ImageTags 
            on Tags.id=ImageTags.tagid 
            inner join Images 
            on ImageTags.imageid=Images.id
            inner join Albums 
            on Images.album = Albums.id 
            INNER join AlbumRoots 
            on AlbumRoots.id = Albums.albumRoot 
            where Tags.pid=4 and  Tags.id=29
        """)

        faces = cursor.fetchall()
        conn.close()
    except Exception as e:
        print(f"Erreur lors de la lecture de la base de données Digikam: {e}")
    return faces

# Fonction pour vérifier si un fichier existe sur le montage NFS
def check_file_exists_on_nfs(file_path):
    return Path(file_path).exists()

# Fonction pour ajouter un tag à un fichier sur Nextcloud
def add_tag_to_nextcloud(file_path, tags):
    try:
        headers = {
            'OCS-APIRequest': 'true',
            'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept-Charset' : 'utf-8',
        }

        # URL de l'API Nextcloud pour ajouter un tag
        url = f'{NEXTCLOUD_URL}/index.php/apps/files/api/v1/files/tags'

        # Ajouter plusieurs tags
        for tag in tags:
            # Exécution de l'API pour chaque tag
            response = requests.post(url, data={'tag': tag, 'path': file_path}, headers=headers, auth=HTTPBasicAuth(NEXTCLOUD_USER, NEXTCLOUD_PASSWORD))
            if response.status_code == 200:
                print(f'Tag "{tag}" ajouté avec succès à {file_path}')
            else:
                print(f'Erreur lors de l\'ajout du tag "{tag}" à {file_path}: {response.status_code}')
    except Exception as e:
        print(f"Erreur lors de l'ajout du tag à Nextcloud: {e}")

# Fonction pour extraire le label des visages et appliquer les tags
def process_faces_and_apply_tags():
    faces = get_faces_from_digikam()

    if not faces:
        print("Aucun visage trouvé dans Digikam.")
        return

    for face in faces:
        tagId, tagName, albumRoot, specificPath, relativePath, name = face

        # Extraire les paramètres
        query = urlparse(albumRoot).query
        params = parse_qs(query)

        # Récupérer mountpath
        mountpath = params.get("mountpath", [""])[0]


        # Vérifier si part1 et part2 ne contiennent que des "/"
        specificPath_valid = specificPath.strip("/") if specificPath else ""
        relativePath_valid = relativePath.strip("/") if relativePath else ""

        # Construire le chemin final
        parts = [mountpath, specificPath_valid, relativePath_valid, name]
        file_path = "/".join(filter(None, parts))  # Élimine les parties vides et joint avec "/"

        if not check_file_exists_on_nfs(file_path):
            print(f'Fichier non trouvé sur le montage NFS: {file_path}')
            continue

        # Préparer les tags à ajouter
        tags = []

        if tagName:
            tags.append(tagName)  # Ajouter le label Digikam comme tag
        else:
            tags.append("unknown_face")  # Tag par défaut pour les visages sans label

        # Appliquer les tags à Nextcloud
        add_tag_to_nextcloud(file_path, tags)

# Fonction pour traiter les fichiers dans le montage NFS
def process_photos():
    print(sys.getdefaultencoding())  # Doit afficher "utf-8"
    print(locale.getpreferredencoding())  # Doit afficher "UTF-8"
    try:
        print("Démarrage du traitement des photos...")

        process_faces_and_apply_tags()

    except Exception as e:
        print(f"Erreur générale lors du traitement des photos: {e}")

# Exécution du script
if __name__ == "__main__":
    process_photos()