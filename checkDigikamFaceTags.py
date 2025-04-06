import json
import time
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import aliased
from digikam4_model import Tags, ImageTagProperties, Images, Albums


# ImageTagProperties NON CONFIRME
# property = autodetectedFace, autodetectedPerson, ignoredFace
# ImageTagProperties A SYNCHRONISER
# property = tagRegion

def check_person_unicity_for_digikam(dgk_session):
    debut = time.time()

    number = 0
    has_problem = False

    # Lister les Tags dont Tags.pid=4 (person)
    TagsPeople = aliased(Tags)
    dgk_tags = (
        dgk_session.query(Tags)
        .join(TagsPeople, Tags.pid == TagsPeople.id)
        .filter(TagsPeople.name == 'People')
        .filter(~Tags.name.in_(['Unknown', 'Ignored', 'Unconfirmed']))
    )

    person_dict = dict()

    for dgk_tag in dgk_tags:
        number = number + 1
        person = person_dict.get(dgk_tag.name)
        if person is None:
            person_dict[dgk_tag.name] = dgk_tag.name
        else:
            print("checkPersonUnicity : Doublon : " + dgk_tag.name)
            has_problem = True

    print("checkPersonUnicity : " + time.ctime(time.time() - debut)[11:19])

    return has_problem


def check_person_unicity_for_each_image(dgk_session):
    debut = time.time()
    has_problem = False
    number = 0

    duplicates = (
        dgk_session.query(
            ImageTagProperties.imageid,
            ImageTagProperties.tagid,
            Albums.relativePath,
            Images.name,
            Tags.name,
            func.count().label("count")
        )
        .filter(ImageTagProperties.property == "tagRegion")
        .join(Images, Images.id == ImageTagProperties.imageid)
        .join(Albums, Albums.id == Images.album)
        .join(Tags, Tags.id == ImageTagProperties.tagid)
        .group_by(ImageTagProperties.imageid, ImageTagProperties.tagid, Albums.relativePath, Images.name, Tags.name)
        .having(func.count() > 1)
        .all()
    )

    for imageid, tagid, image_path, image_name, person, count in duplicates:
        has_problem = True
        number = number + 1
        print("Doublons pour :" + person + " : sur l'image : " + image_path + "/" + image_name)

    print("checkPersonUnicityForEachImage : " + time.ctime(time.time() - debut)[11:19])

    return has_problem
