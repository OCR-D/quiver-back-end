"""
In our resulting `ocrd_all_release.json` each project (= submodule of ocrd_all)
should appear only once – listed under the most recent ocrd_all release it is part of.

Therefore we filter all Release objects after their creation to determine if their projects
are mentioned for the first time (making the current release the most recent one) or if 
they have already been mentioned (which means that a more recent ocrd_all release also
contains the project). A project is kept in the first case while it is tossed in the latter.

If a Release object has an empty projects attribute, it is tossed completely.
"""
def filter_release_projects(releases):
    released_projects = []
    filtered_releases = []

    for release in releases:
        filtered_projects = []

        for project in release.projects:
            if project not in released_projects:
                filtered_projects.append(project)
                released_projects.append(project)

        if filtered_projects:
            new_release_object = {}
            new_release_object['tag'] = release.tag
            new_release_object['projects'] = filtered_projects
            filtered_releases.append(new_release_object)

    return filtered_releases
