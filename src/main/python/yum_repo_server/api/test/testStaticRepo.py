import httplib
import unittest
import os
from yum_repo_client.repoclient import RepoException
from yum_repo_client.repoclient import HttpClient 
from yum_repo_server.test import Constants, unique_repo_name
from yum_repo_server.test.baseIntegrationTestCase import BaseIntegrationTestCase
import httplib2
from yum_repo_server.settings import REPO_CONFIG


class TestStaticRepo(BaseIntegrationTestCase):
    def test_get_directory_listing(self):
        reponame = self.createNewRepoAndAssertValid()
        virtual_reponame = Constants.TESTREPO_PREFIX + reponame
        self.create_virtual_repo_from_static_repo(virtual_reponame, reponame)
        response = self.helper.do_http_get(Constants.HTTP_PATH_STATIC + '/')
        self.assertEquals(response.status, httplib.OK, "Returncode for http GET must be 200 OK, but was" + str(response.status))
        msg = response.read()
        self.assertTrue(reponame in msg, "Newly created repo should be listed on a GET")


    def test_post_with_no_data(self):
        response = self.doHttpPost(Constants.HTTP_PATH_STATIC + '/', None)
        self.assertEquals(response.status, httplib.BAD_REQUEST, "Returncode for post without data must be BAD REQUEST, but was" + str(response.status))
        self.assertEquals(response.read(), Constants.API_MSG_NO_POSTDATA,
            "Response for post without data must be " + Constants.API_MSG_NO_POSTDATA)


    def test_post_without_name(self):
        response = self.doHttpPost(Constants.HTTP_PATH_STATIC + '/', 'foo=bar')
        self.assertEquals(response.status, httplib.BAD_REQUEST,
            "Response for post without name in data must be BAD REQUEST")
        msg = response.read()
        self.assertEquals(msg, Constants.API_MSG_NO_NAME_IN_POSTDATA,
            "Response for post without name in data must be " + Constants.API_MSG_NO_NAME_IN_POSTDATA)


    def test_post_with_forbidden_repo_name(self):
        response = self.doHttpPost(Constants.HTTP_PATH_STATIC + '/', 'name=../directorytraversal')
        self.assertEquals(response.status, httplib.BAD_REQUEST, "Response for name violating regex must be BAD REQUEST, but was" + str(response.status))
        msg = response.read()
        self.assertEquals(msg, Constants.API_MSG_REGEX_MISMATCH,
            "Response for name violating regex must be " + Constants.API_MSG_REGEX_MISMATCH)


    def test_post_with_valid_repo_name(self):
        self.createNewRepoAndAssertValid()


    def test_post_with_duplicate_repo_name(self):
        reponame = unique_repo_name()
        self.doHttpPost(Constants.HTTP_PATH_STATIC + '/', "name=" + reponame)
        response = self.doHttpPost(Constants.HTTP_PATH_STATIC + '/', "name=" + reponame) #double POST -> repo already exists
        self.assertEquals(response.status, httplib.CONFLICT, "Response for duplicate repo name must be CONFLICT, but was" + str(response.status))
        msg = response.read()
        expected = Constants.API_MSG_DUPLICATE_PREFIX + reponame + Constants.API_MSG_DUPLICATE_SUFFIX
        self.assertEqual(msg, expected,
            "Response for duplicate repo name must be " + Constants.API_MSG_DUPLICATE_PREFIX + reponame + Constants.API_MSG_DUPLICATE_SUFFIX)

    def test_delete_repo_returns_bad_request_when_switch_is_false(self):
        REPO_CONFIG['static_repo_deletable'] = False
        reponame = unique_repo_name()
        
        self.repoclient().createStaticRepo(reponame)
        response = self.repoclient().doHttpDelete('/repo/%s' % reponame)
        self.assertEqual(httplib.BAD_REQUEST, response.status)

    def test_delete_repo(self):
        REPO_CONFIG['static_repo_deletable'] = True
        reponame = unique_repo_name()
        
        self.repoclient().createStaticRepo(reponame)
        self.repoclient().delete_static_repo(reponame)
        
        response = self.helper.do_http_get('/repo/%s' % reponame)
        self.assertEqual(httplib.NOT_FOUND, response.status)
        
    def test_delete_not_existing_repo(self):
        REPO_CONFIG['static_repo_deletable'] = True
        response = self.repoclient().doHttpDelete('/repo/i_should_not_exist')
        self.assertEqual(httplib.NOT_FOUND, response.status)
        
    def test_delete_returns_bad_request_when_a_reponame_with_slash_is_given(self):
        REPO_CONFIG['static_repo_deletable'] = True
        response = self.repoclient().doHttpDelete('/repo/bad/repo/name')
        self.assertEqual(httplib.BAD_REQUEST, response.status)
        
    def test_delete_returns_bad_request_when_reponame_is_parent_dir(self):
        REPO_CONFIG['static_repo_deletable'] = True
        # try to delete all repositories.
        response = self.repoclient().doHttpDelete('/repo/..')
        self.assertEqual(httplib.BAD_REQUEST, response.status)

    def test_delete_returns_bad_request_when_reponame_is_dot(self):
        REPO_CONFIG['static_repo_deletable'] = True
        # try to delete all repositories.
        response = self.repoclient().doHttpDelete('/repo/.')
        self.assertEqual(httplib.BAD_REQUEST, response.status)

    def test_upload_rpm_to_repo(self):
        repo_name = self.createNewRepoAndAssertValid()
        testRPMFilePath = Constants.TEST_RPM_FILE_LOC + Constants.TEST_RPM_FILE_NAME
        self.upload_testfile(repo_name, testRPMFilePath)
        repo_path = self.determine_repo_path(repo_name)
        uploaded_file_path = repo_path + Constants.TEST_RPM_DESTINATION_NAME
        self.assertTrue(os.path.isfile(uploaded_file_path))


    def given_rpm_in_repository(self, repo_name):
        testRPMFilePath = Constants.TEST_RPM_FILE_LOC + Constants.TEST_RPM_FILE_NAME
        self.upload_testfile(repo_name, testRPMFilePath)
        repo_path = self.determine_repo_path(repo_name)
        uploaded_file_path = repo_path + Constants.TEST_RPM_DESTINATION_NAME
        self.assertTrue(os.path.isfile(uploaded_file_path))
        return uploaded_file_path

    def test_remove_rpm_from_repo(self):
        repo_name = self.createNewRepoAndAssertValid()
        uploaded_file_path = self.given_rpm_in_repository(repo_name)

        httpResponse = self.repoclient().deleteSingleRpm(repo_name, Constants.TEST_RPM_DESTINATION_NAME)
        self.assertStatusCode(httpResponse, httplib.NO_CONTENT)
        self.assertFalse(os.path.isfile(uploaded_file_path))

    def test_remove_rpm_in_non_existing_repository(self):
        self.assertRaises(RepoException, self.repoclient().deleteSingleRpm, "i_dont_think_this_exists", Constants.TEST_RPM_DESTINATION_NAME)

    def test_remove_non_existing_rpm_from_existing_repository(self):
        repo_name = self.createNewRepoAndAssertValid()
        self.assertRaises(RepoException, self.repoclient().deleteSingleRpm, repo_name, Constants.TEST_RPM_DESTINATION_NAME)

    def test_remove_rpm_with_bad_path(self):
        repo_name = self.createNewRepoAndAssertValid()
        self.assertRaises(RepoException, self.repoclient().deleteSingleRpm, repo_name, '/../' + Constants.TEST_RPM_DESTINATION_NAME)

    def test_remove_rpm_for_whole_arch_is_not_allowed(self):
        repo_name = self.createNewRepoAndAssertValid()
        self.assertRaises(RepoException, self.repoclient().deleteSingleRpm, repo_name, '/noarch/')

    def test_base_directory_listing(self):
        repo_name = self.createNewRepoAndAssertValid()
        self.create_virtual_repo_from_static_repo(unique_repo_name(), repo_name)
        response = self.helper.do_http_get("/repo/")
        self.assertStatusCode(response, httplib.OK)
        msg = response.read()
        self.assertTrue(repo_name in msg)
        self.assertTrue('virtual/' in msg)

    def test_generate_meta_should_fail_for_not_existing_repos(self):
        repo_name = unique_repo_name()
        self.assertRaises(RepoException, self.repoclient().generateMetadata, repo_name)
        
    def test_download_of_repo_md_xml(self):
        reponame = self.createNewRepoAndAssertValid()
        testRPMFilePath = Constants.TEST_RPM_FILE_LOC + Constants.TEST_RPM_FILE_NAME
        self.repoclient().uploadRpm(reponame, testRPMFilePath)
        self.repoclient().generateMetadata(reponame)
        response = self.helper.do_http_get("/repo/" + reponame + '/repodata/repomd.xml')
        
        self.assertStatusCode(response, httplib.OK)
        
    def test_should_not_create_repo(self):
        reponame = unique_repo_name()
        testRPMFilePath = Constants.TEST_RPM_FILE_LOC + Constants.TEST_RPM_FILE_NAME
        self.assertRaises(RepoException, HttpClient.uploadRpm, self.repoclient(), reponame, testRPMFilePath)

if __name__ == '__main__':
    unittest.main()

    