# Django Change List

An app to scrape and list the Django Release Notes: 
 [https://docs.djangoproject.com/en/3.0/releases/][here]

[here]: https://docs.djangoproject.com/en/3.0/releases/

Creates a searchable list for developers upgrading their code.

It also has the capacity to export in various file formats, including Jira compatible views.

## Installation

1. Install from Git
    ``` shell script
    pip install -e git+https://github.com/mcldev/django-change-list#egg=django-change-list
    ```
2. Add the following settings:
    * Installed Apps in Settings:
    ```python
    INSTALLED_APPS = [...
        'versionfield',
        'crispy_forms',
        'requests',
        'bs4',
        'sekizai',
        'django_change_list',
   ...]
    ```
    * Add the Change Views URLS under any path, e.g. `changes/`:
    ```python
    urlpatterns = [ 
       ...
        path('changes/', include('django_change_list.urls')),
       ...
    ]
    ```
   * Configure your app and other settings, e.g. Database etc.
 
3. Run `python manage.py makemigrations` and `python manage.py migrate`  

4. Run and query to load all changes. Each query will dynamically load any missing or new changes as they appear.
