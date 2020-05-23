from enum import Enum


class CHANGE_TYPES(Enum):
    NEW_FEATURES = 0
    BUG_FIXES = 1
    BACKWARDS_INCOMPATIBLE = 2
    DEPRECATED = 3
    REMOVED = 4


HTML_LOOKUPS = {
    CHANGE_TYPES.NEW_FEATURES: "s-what-s-new-in-django-{ver}",
    CHANGE_TYPES.BUG_FIXES: "s-bugfixes",
    CHANGE_TYPES.BACKWARDS_INCOMPATIBLE: "s-backwards-incompatible-changes-in-{ver}",
    CHANGE_TYPES.DEPRECATED: "s-features-deprecated-in-{ver}",
    CHANGE_TYPES.REMOVED: "s-features-removed-in-{ver}",
}

CHANGE_TYPE_STR = 'change_type_'


def change_type_to_field_name(change_type):
    return "{}{}".format(CHANGE_TYPE_STR, change_type.name.lower())


def field_name_to_change_type(field_name):
    return CHANGE_TYPES["{}".format(field_name.replace(CHANGE_TYPE_STR, '').upper())]


def all_change_types():
    return [a.value for a in list(CHANGE_TYPES)]


def all_change_names():
    return [a.name for a in list(CHANGE_TYPES)]


def change_select_list():
    return [(chg.value, chg.name) for chg in CHANGE_TYPES]


def get_version(version_txt):
    return "{}-{}".format(*version_txt.split(".")[:2])


def get_html_lookup(version_txt, change_type):
    ver = get_version(version_txt)
    return HTML_LOOKUPS[change_type].format(ver=ver)


def get_css_name(change_type):
    if change_type == CHANGE_TYPES.REMOVED or \
            change_type == CHANGE_TYPES.DEPRECATED:
        return "table-danger"
    if change_type == CHANGE_TYPES.BACKWARDS_INCOMPATIBLE:
        return "table-warning"
    if change_type == CHANGE_TYPES.NEW_FEATURES:
        return "table-success"
    if change_type == CHANGE_TYPES.BUG_FIXES:
        return "table-secondary"


def get_jira_issue_type(change_type):
    if change_type == CHANGE_TYPES.REMOVED or \
            change_type == CHANGE_TYPES.DEPRECATED:
        return "bug"
    if change_type == CHANGE_TYPES.BACKWARDS_INCOMPATIBLE:
        return "task"
    if change_type == CHANGE_TYPES.NEW_FEATURES:
        return "story"
    if change_type == CHANGE_TYPES.BUG_FIXES:
        return "story"
