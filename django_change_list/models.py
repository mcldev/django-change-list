from django.db import models
from django.utils.safestring import mark_safe

from .consts import *
from versionfield import VersionField, Version


class ReleaseModel(models.Model):
    version_txt = models.CharField('Version Number', max_length=20)
    version = VersionField(verbose_name='Version as Int')
    version_link = models.URLField('Link to Version Release Notes')

    def save(self, *args, **kwargs):
        if not self.version:
            self.version = Version(self.version_txt)
        super(ReleaseModel, self).save(*args, **kwargs)


class ChangeModel(models.Model):
    release = models.ForeignKey(ReleaseModel, on_delete=models.CASCADE, related_name="releases")
    change_link = models.URLField('Link to Change Notes')
    change_type = models.IntegerField('Change Type')

    summary = models.CharField('Change Summary', max_length=100)
    details_html = models.TextField('Change Details in HTML')
    details_text = models.TextField('Change Details in Plain Text')

    def save(self, *args, **kwargs):
        self.summary = self.summary.replace('\n', '')[:99]
        self.details_html = self.details_html.replace('\n', '')
        self.details_text = self.details_text.replace('\n', '')
        super(ChangeModel, self).save(*args, **kwargs)

    @property
    def get_change_type(self):
        return CHANGE_TYPES(self.change_type).name

    @property
    def get_css_name(self):
        return get_css_name(CHANGE_TYPES(self.change_type))

    @property
    def get_release_version(self):
        return self.release.version_txt

    @property
    def get_release_version_int(self):
        return int(self.release.version)

    @property
    def get_jira_issue_type(self):
        return get_jira_issue_type(CHANGE_TYPES(self.change_type))

    @property
    def get_jira_summary(self):
        return "{type} [{ver}] - {summary}".format(type=self.get_change_type,
                                                  ver=self.get_release_version,
                                                  summary=self.summary[:45])

    @property
    def get_jira_description(self):
        return mark_safe("*Release Version*: {ver} \n" \
                         "*Change Type*: {type} \n" \
                         "*Change URL*: [{url}|{url}] \n" \
                         "*Change Details*: \n" \
                         "{details}".format(ver=self.get_release_version,
                                            type=self.get_change_type,
                                            url=self.change_link,
                                            details=self.details_text))

    @classmethod
    def get_vue_table_columns(cls):
        cols = [
            {'title': 'Version',
             'field': 'get_release_version'},
            {'title': 'Change Type',
             'field': 'get_change_type'},
            {'title': 'CSS Name',
             'field': 'get_css_name'},
            {'title': 'Release Version (Int)',
             'field': 'get_release_version_int'},
            {'title': 'Jira Issue Type',
             'field': 'get_jira_issue_type'}
        ]
        cols += [{'title': f.verbose_name, 'field': f.name} for f in cls._meta.fields if f.name != 'release']

        return cols

    @classmethod
    def get_vue_fields(cls):
        return [f['field'] for f in cls.get_vue_table_columns()]

    @classmethod
    def get_jira_columns(cls):
        return [
            {'title': 'Issue Type',
             'field': 'get_jira_issue_type'},
            {'title': 'Summary',
             'field': 'get_jira_summary'},
            {'title': 'Description',
             'field': 'get_jira_description'},
        ]
