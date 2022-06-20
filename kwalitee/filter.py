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
    