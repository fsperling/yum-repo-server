import os
import shutil
from yum_repo_server.api.services.repoConfigService import RepoConfigService
from unittest import TestCase


class TestRepoConfigService(TestCase):
    targetDir = os.getcwd() + '/target/static/test-cleanup-dir'
    testRepo = targetDir + '/noarch'
    rpm_file_names = ['rss-4-1.2.noarch.rpm',
                      'rss-5-1.1.noarch.rpm',
                      'rss-7-1.4.noarch.rpm',
                      'rss-4-1.1.noarch.rpm']

    def test_doCleanup(self):
        os.makedirs(self.testRepo)
        self.touchRpms(self.testRepo)

        try:
            RepoConfigService().doCleanup(self.targetDir, 3)
            self.assertFalse(os.path.exists(self.testRepo + '/rss-4-1.1.noarch.rpm'))
        finally:
            shutil.rmtree(self.targetDir)
            
    def test_do_not_remove_rpms_when_rpm_max_keep_is_zero(self):
        os.makedirs(self.testRepo)
        self.touchRpms(self.testRepo)

        try:
            RepoConfigService().doCleanup(self.targetDir, 0)
            self.assertTrue(os.path.exists(self.testRepo + '/rss-4-1.1.noarch.rpm'), 'rpm-file was deleted.')
        finally:
            shutil.rmtree(self.targetDir)
        
    def test_do_cleanup_should_raise_valueError_when_rpm_max_keep_is_not_an_integer(self):
        try:
            RepoConfigService().doCleanup(self.targetDir, '3')
            self.fail('do cleanup should check, that rpm_max_keep is an integer.')
        except ValueError:
            pass

    def test_find_rpms_to_delete(self):
        rpm_file_names = ['rss-4-1.1.noarch.rpm',
                          'rss-4-1.2.noarch.rpm',
                          'rss-5-1.1.noarch.rpm',
                          'rss-7-1.4.noarch.rpm']
        
        rpm_to_delete = RepoConfigService()._find_rpms_to_delete(rpm_file_names, 3)
        
        self.assertEquals(1, len(rpm_to_delete))
        self.assertEquals('rss-4-1.1.noarch.rpm', rpm_to_delete[0].file_name)
        
    def test_find_rpms_to_delete_returns_empty_list_when_single_group_is_not_big_enough(self):
        rpm_file_names = ['rss-4-1.1.noarch.rpm',
                          'rss-4-1.2.noarch.rpm',
                          'rss-5-1.1.noarch.rpm',
                          'rss-feed-7-1.4.noarch.rpm']
        
        rpm_to_delete = RepoConfigService()._find_rpms_to_delete(rpm_file_names, 3)
        
        self.assertEquals(0, len(rpm_to_delete))

    def touchRpms(self, testRepo):
        for repo in self.rpm_file_names:
            open(testRepo + '/' + repo, 'w').close()
