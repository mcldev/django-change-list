from django import forms
from crispy_forms.helper import FormHelper

from .consts import *
from .utils import get_release_urls


all_releases = get_release_urls()
version_select_list = [(ver[1], ver[1]) for ver in all_releases]

class ChangesForm(forms.Form):
    from_version = forms.CharField(label='Current Version', max_length=100, initial="1.11",
                                   widget=forms.Select(choices=version_select_list))
    to_version = forms.CharField(label='New Version', max_length=100, initial="2.2",
                                    widget=forms.Select(choices=version_select_list))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.helper = FormHelper(self)
        for change_type in CHANGE_TYPES:
            field_name = change_type_to_field_name(change_type)
            default_value = change_type.value >= 3
            self.fields[field_name] = forms.BooleanField(label=change_type.name, required=False, initial=default_value)


    def clean(self):
        change_types = []
        for change_type in CHANGE_TYPES:
            field_name = '{}{}'.format(CHANGE_TYPE_STR, change_type.name.lower())
            value = self.cleaned_data.get(field_name)
            if value:
                change_types.append(change_type.value)

        self.cleaned_data["change_types"] = change_types


class ChangesVueForm(ChangesForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.vue_init_data = {'change_types': []}

        for field_name in self.fields:
            if field_name.startswith(CHANGE_TYPE_STR):
                change_type = field_name_to_change_type(field_name)
                self.fields[field_name].widget.attrs = {'v-model': 'change_types', 'value': change_type.name}
                if self.fields[field_name].initial:
                    self.vue_init_data['change_types'].append(change_type.name)
            else:
                self.fields[field_name].widget.attrs['v-model'] = field_name
                self.vue_init_data[field_name] = self.fields[field_name].initial
