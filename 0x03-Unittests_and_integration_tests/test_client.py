#!/usr/bin/env python3
"""Unit tests for client module.
"""
import unittest

from parameterized import parameterized, parameterized_class
from unittest.mock import patch, Mock, PropertyMock

from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient.
    """

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test GithubOrgClient.org returns correct value and calls get_json.
        """
        test_payload = {
            "name": org_name,
            "repos_url": f"https: //api.github.com/orgs/{org_name}/repos"
        }
        mock_get_json.return_value = test_payload
        client = GithubOrgClient(org_name)
        result = client.org
        self.assertEqual(result, test_payload)
        url = f"https: //api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(url)

    def test_public_repos_url(self):
        """Test GithubOrgClient._public_repos_url returns expected URL.
        """
        test_payload = {
            "repos_url": "https: //api.github.com/orgs/test_org/repos"
        }
        with patch('client.GithubOrgClient.org',
                   new_callable=PropertyMock) as mock_org:
            mock_org.return_value = test_payload
            client = GithubOrgClient("test_org")
            result = client._public_repos_url
            self.assertEqual(result, test_payload["repos_url"])

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test GithubOrgClient.public_repos returns expected repo names.
        """
        test_payload = [
            {"name": "repo1"},
            {"name": "repo2"}
        ]
        test_url = "https://api.github.com/orgs/test_org/repos"
        mock_get_json.return_value = test_payload
        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock) as mock_repos_url:
            mock_repos_url.return_value = test_url
            client = GithubOrgClient("test_org")
            result = client.public_repos()
            self.assertEqual(result, ["repo1", "repo2"])
            mock_get_json.assert_called_once_with(test_url)
            mock_repos_url.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test GithubOrgClient.has_license returns correct boolean.
        """
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class([
    {
        "org_payload": org_payload,
        "repos_payload": repos_payload,
        "expected_repos": expected_repos,
        "apache2_repos": apache2_repos
    } for org_payload, repos_payload, expected_repos, apache2_repos
    in TEST_PAYLOAD
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.
    """

    @classmethod
    def setUpClass(cls):
        """Set up class by mocking requests.get with fixture payloads.
        """
        def get_side_effect(url):
            mock_response = Mock()
            if url == "https: //api.github.com/orgs/google":
                mock_response.json.return_value = cls.org_payload
            elif url == cls.org_payload["repos_url"]:
                mock_response.json.return_value = cls.repos_payload
            return mock_response

        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()
        cls.mock_get.side_effect = get_side_effect

    @classmethod
    def tearDownClass(cls):
        """Tear down class by stopping the patcher.
        """
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos returns expected repos.
        """
        client = GithubOrgClient("google")
        result = client.public_repos()
        self.assertEqual(result, self.expected_repos)


if __name__ == '__main__':
    unittest.main()
