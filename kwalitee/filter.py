def filter_release_projects(releases):
    released_projects = []
    filtered_releases = []

    for release in releases:
        #print('\n\n#################')
        #print(release)
        filtered_projects = []

        for project in release.projects:
            if (project in released_projects):
                pass
            else:
                filtered_projects.append(project)
                released_projects.append(project)

        #print(f'\nfiltered projects: {filtered_projects}')
        #print(f'\nreleased projects: {released_projects}')

        if filtered_projects:
            new_release_object = {}
            new_release_object['tag'] = release.tag
            new_release_object['projects'] = filtered_projects
            filtered_releases.append(new_release_object)

    return filtered_releases

        #print(f'\nfiltered releases: {filtered_releases}')