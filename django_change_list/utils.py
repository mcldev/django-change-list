import requests
import urllib.request
import time
from bs4 import BeautifulSoup
from versionfield import Version

from .models import ReleaseModel, ChangeModel
from .consts import *


def clean_string(element, return_str=True, base_url=None):
    if not element:
        return

    if return_str:
        str = element.text
    else:
        if base_url:
            for a in element.findAll('a'):
                if not a['href'].startswith('http'):
                    base_url = base_url if base_url.endswith('/') else base_url + '/'
                    a['href'] = "{}{}".format(base_url, a['href'])
                    a['target'] = "_blank"
        str = element.prettify()

    encoded_string = str.encode("ascii", "ignore")
    decode_string = encoded_string.decode()
    str = decode_string.replace('\n', ' ').strip()

    return str


def get_release_urls():
    url = 'https://docs.djangoproject.com/en/3.0/releases/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    release_id = 's-final-releases'
    sections = soup.find("body").find("div", {"id": release_id}).find_all("div", {"class": "section"})
    links_and_versions = []
    for section in sections:
        version_urls = section.find_all("li")
        for version_url in version_urls:
            href = version_url.find("a", href=True)
            version_number = href.text.split(' ')[1]
            if version_number == 'version':
                break
            link = "{}{}".format(url, href['href'])
            links_and_versions.append((link, version_number))

    links_and_versions = sorted(links_and_versions, key=lambda l_v: Version(l_v[1]))

    return links_and_versions


def get_changes(from_version=None, to_version=None, change_types=None, force_rebuild=False):
    # Get the latest version of all current versions
    all_releases = get_release_urls()
    change_types = change_types or all_change_types()

    query_versions = []

    for link_version in all_releases:
        link = link_version[0]
        version_number = link_version[1]
        get_version = None

        if from_version and to_version:
            if Version(from_version) < Version(version_number) <= Version(to_version):
                get_version = version_number
        else:
            get_version = version_number

        if get_version:
            # Get rows if missing
            release_model, created = ReleaseModel.objects.get_or_create(version_txt=get_version, version_link=link)

            if not created and force_rebuild:
                ChangeModel.objects.filter(release=release_model).delete()

            if created or force_rebuild:
                print('Getting changes for version: {}'.format(get_version))
                # Get's changes for all change types
                get_changes_for_version(release_model)
                release_model.save()

            # Add to bulk query list
            query_versions.append(release_model)

    # Query DB and get all changes
    return ChangeModel.objects.filter(release__in=query_versions, change_type__in=change_types). \
        order_by('release__version').select_related('release')


# main_section <NEW FEATURES, ...>
#   change_section <Minor features, ...> H3 + link
#       sub_section <django.contrib.postgres,...> H4 - external link (ignore?)
#           list:
#               element[s] <"The new ordering argument...", >
#           element[s] <"The new ordering argument...", >
#   change_section <Model Meta.ordering.., ...> H3 + link
#       list:
#           element[s] <"The new ordering argument...", >
#       element: "To simplify a few parts of Django’s database..."
#
#    list:
#       element[s] <"The new ordering argument...", >
#    element[s] <"The new ordering argument...", >

def recursive_find_sections(release_model, change_type, section, heading, link, heading_level=2):
    ret = []
    sub_sections = section.find_all("div", {"class": "section"}, recursive=False)
    base_link = link.split('#')[0]

    if sub_sections:
        heading_level += 1
        for sect in sub_sections:
            sect_heading = sect.find("h{}".format(heading_level))
            if sect_heading:
                sect_heading = clean_string(sect_heading) or heading
            sect_id = sect["id"]
            if sect_id:
                link = base_link + "#{}".format(sect_id)
            ret += recursive_find_sections(release_model, change_type, sect, sect_heading, link, heading_level)
    else:
        list_sections = section.find_all("ul", recursive=False)
        if list_sections:
            for lst in list_sections:
                list_items = lst.find_all("li", recursive=False)
                for list_item in list_items:
                    ret += recursive_find_sections(release_model, change_type, list_item, heading, link, heading_level)
        else:
            summary = clean_string(section)[:99]
            if heading and not summary.startswith(heading):
                summary = "{} - {}".format(heading, summary)
            details_html = clean_string(section, False, base_link)
            details_text = clean_string(section)

            ret.append(ChangeModel(release=release_model,
                                   change_link=link,
                                   change_type=change_type.value,
                                   summary=summary,
                                   details_html=details_html,
                                   details_text=details_text))

    return ret



def get_changes_for_version(release_model):
    changes = []

    link = release_model.version_link
    version_txt = release_model.version_txt

    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")

    for change_type in CHANGE_TYPES:
        change_lookup = get_html_lookup(version_txt, change_type)

        main_change_sections = soup.find("body").find("div", {"id": change_lookup})
        if not main_change_sections:
            print('\tNo changes for type: {} version: {}'.format(change_type.name, version_txt))
            continue

        # Section: Deprecated, Bug Fixes, New Features etc.
        main_section_link = "{}#{}".format(link, main_change_sections["id"])

        changes = recursive_find_sections(release_model, change_type, main_change_sections, "", main_section_link)

        print('\tLoading {} changes for type: {} version: {}'.format(len(changes), change_type.name, version_txt))

        ChangeModel.objects.bulk_create(changes)
