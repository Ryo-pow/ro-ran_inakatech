import unittest

from flask import json

from openapi_server.models.auth_register_post200_response import AuthRegisterPost200Response  # noqa: E501
from openapi_server.models.token_response import TokenResponse  # noqa: E501
from openapi_server.models.tree import Tree  # noqa: E501
from openapi_server.models.trees_post_request import TreesPostRequest  # noqa: E501
from openapi_server.models.trees_tree_id_lidar_delete200_response import TreesTreeIdLidarDelete200Response  # noqa: E501
from openapi_server.models.trees_tree_id_lidar_post201_response import TreesTreeIdLidarPost201Response  # noqa: E501
from openapi_server.models.trees_tree_id_worklogs_post_request import TreesTreeIdWorklogsPostRequest  # noqa: E501
from openapi_server.models.user_login import UserLogin  # noqa: E501
from openapi_server.models.user_register import UserRegister  # noqa: E501
from openapi_server.models.work_log import WorkLog  # noqa: E501
from openapi_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_auth_login_post(self):
        """Test case for auth_login_post

        Login user and get JWT
        """
        user_login = {"password":"password","username":"username"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/v1/auth/login',
            method='POST',
            headers=headers,
            data=json.dumps(user_login),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_auth_register_post(self):
        """Test case for auth_register_post

        Register a new user
        """
        user_register = {"password":"password","username":"username"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/v1/auth/register',
            method='POST',
            headers=headers,
            data=json.dumps(user_register),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_trees_get(self):
        """Test case for trees_get

        List all trees
        """
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/v1/trees',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_trees_post(self):
        """Test case for trees_post

        Create a new tree
        """
        trees_post_request = openapi_server.TreesPostRequest()
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/v1/trees',
            method='POST',
            headers=headers,
            data=json.dumps(trees_post_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_trees_tree_id_get(self):
        """Test case for trees_tree_id_get

        Get tree details
        """
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/v1/trees/{tree_id}'.format(tree_id=56),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_trees_tree_id_lidar_delete(self):
        """Test case for trees_tree_id_lidar_delete

        Delete LiDAR file
        """
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/v1/trees/{tree_id}/lidar'.format(tree_id=56),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_trees_tree_id_lidar_head(self):
        """Test case for trees_tree_id_lidar_head

        Get LiDAR file metadata
        """
        headers = { 
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/v1/trees/{tree_id}/lidar'.format(tree_id=56),
            method='HEAD',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    @unittest.skip("multipart/form-data not supported by Connexion")
    def test_trees_tree_id_lidar_post(self):
        """Test case for trees_tree_id_lidar_post

        Upload LiDAR file for a tree
        """
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'multipart/form-data',
            'Authorization': 'Bearer special-key',
        }
        data = dict(file='/path/to/file')
        response = self.client.open(
            '/api/v1/trees/{tree_id}/lidar'.format(tree_id=56),
            method='POST',
            headers=headers,
            data=data,
            content_type='multipart/form-data')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_trees_tree_id_worklogs_get(self):
        """Test case for trees_tree_id_worklogs_get

        List work logs for a tree
        """
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/v1/trees/{tree_id}/worklogs'.format(tree_id=56),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_trees_tree_id_worklogs_post(self):
        """Test case for trees_tree_id_worklogs_post

        Add a new work log
        """
        trees_tree_id_worklogs_post_request = openapi_server.TreesTreeIdWorklogsPostRequest()
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/v1/trees/{tree_id}/worklogs'.format(tree_id=56),
            method='POST',
            headers=headers,
            data=json.dumps(trees_tree_id_worklogs_post_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_trees_tree_id_worklogs_worklog_id_get(self):
        """Test case for trees_tree_id_worklogs_worklog_id_get

        Get work log details
        """
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/v1/trees/{tree_id}/worklogs/{worklog_id}'.format(tree_id=56, worklog_id=56),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
