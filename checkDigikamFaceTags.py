import json
import time
from datetime import datetime
from sqlalchemy.orm import aliased
from digikam4_model import Tags, ImageTagProperties, Images, Albums


def check_person_unicity_for_digikam(dgk_session):
    debut = time.time()

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

    images_tag_properties = (dgk_session.query(ImageTagProperties).filter(
        ImageTagProperties.property == 'tagRegion' or ImageTagProperties.property == 'faceToTrain')
    )
    image_tag_dict = dict()

    for imageTagProperties in images_tag_properties:
        image_tag = image_tag_dict.get(imageTagProperties.imageid + "-" + imageTagProperties.tagid)
        if image_tag is None:
            image_tag[imageTagProperties.imageid + "-" + imageTagProperties.tagid] = (
                    imageTagProperties.imageid + "-" + imageTagProperties.tagid)
        else:
            print(
                "checkPersonUnicityForEachImage : Doublon : ImageId=" + imageTagProperties.imageid
                + ", TagId=" + imageTagProperties.tagid)
            has_problem = True

    print("checkPersonUnicityForEachImage : " + time.ctime(time.time() - debut)[11:19])

    return has_problem
