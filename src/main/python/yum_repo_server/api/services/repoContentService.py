import os

from yum_repo_server.api.services.repoConfigService import RepoConfigService

class RepoContentService(object):
    """
        Service to retrieve information about the content of a repository.
    """

    repoConfigService = RepoConfigService()

    def list_packages(self, repository_name):
        """
            @return: a list of tuples (first element is the architecture name, second element is the package file name)
        """
        repository_path = self.repoConfigService.getStaticRepoDir(repository_name)
        available_architectures = os.listdir(repository_path)
        packages_in_repository = []

        for architecture in available_architectures:
            architecture_path = os.path.join(repository_path, architecture)
            packages_in_architecture_dir = os.listdir(architecture_path)

            for package in packages_in_architecture_dir:
                package_path = os.path.join(repository_path, architecture, package)
                packages_in_repository.append((architecture, package_path))

        return packages_in_repository