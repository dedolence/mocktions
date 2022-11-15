from django.test import TestCase
from ..templatetags import breadcrumbs
from django.template import Node, VariableDoesNotExist
from django.template.context import RequestContext
from ..templatetags import breadcrumbs
from unittest import mock
from unittest.mock import patch


class BreadCrumbNodeTest(TestCase):

    @patch('base.templatetags.breadcrumbs.create_crumb', return_value=True)
    def test_title_default(self, mock_create_crumb):
        bcn = breadcrumbs.BreadcrumbNode(["double quote"])
        bcn.render(RequestContext({}))
        mock_create_crumb.assert_called_with('', None)

    @patch('builtins.print')
    def test_URL_exception(self, mock_print):
        bcn = breadcrumbs.BreadcrumbNode(["title", "fake-url"])
        bcn.render(RequestContext({}))
        val = bcn.vars[1]
        mock_print.assert_called_with('URL does not exist', val)


class UrlBreadCrumbNodeTest(TestCase):
    
    @patch('base.templatetags.breadcrumbs.create_crumb', return_value=True)
    def test_title_default(self, mock_create_crumb):
        class Url_Node:
            def render(self, context):
                return True

        bcn = breadcrumbs.UrlBreadcrumbNode(
            'title',
            Url_Node()
        )
        bcn.render(RequestContext({}))
        mock_create_crumb.assert_called_with('', True)