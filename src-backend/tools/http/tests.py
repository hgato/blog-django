import json

from django.http import HttpRequest, JsonResponse
from django.test import TestCase

from tools.http.mixins import JsonMixin


class JsonMixinTest(TestCase):
    def test_clear_body(self):
        """
        Clear body must dump json from request body
        """
        request = HttpRequest()
        expected_body = {'hello': 'world'}
        request._body = json.dumps(expected_body)
        json_mixin = JsonMixin()
        self.assertEqual(expected_body, json_mixin.clean_body(request), 'Wrong body returned')

    def test_check_body_error(self):
        """
        check_body method must raise error if no expected property
        """
        expected = ['field_that_body_does_not_contain']
        body = {'only_body_field': "value"}
        json_mixin = JsonMixin()
        with self.assertRaises(Exception):
            json_mixin.check_body(body, expected)

    def test_check_body_success(self):
        """
        check_body must not raise error if all expected fields exist
        """
        expected = ['only_body_field']
        body = {'only_body_field': "value"}
        json_mixin = JsonMixin()
        self.assertIsNone(json_mixin.check_body(body, expected))

    def test_process_body_not_required(self):
        """
        process body must work as clear_body if not provided second argument
        """
        request = HttpRequest()
        expected_body = {'hello': 'world'}
        request._body = json.dumps(expected_body)
        json_mixin = JsonMixin()
        self.assertEqual(expected_body, json_mixin.process_body(request), 'Wrong body returned')

    def test_process_body_success(self):
        """
        process body must work as clear_body if expected fields are in body
        """
        request = HttpRequest()
        expected = ['only_body_field']
        body = {'only_body_field': "value"}
        request._body = json.dumps(body)
        json_mixin = JsonMixin()
        self.assertEqual(body, json_mixin.process_body(request, expected), 'Wrong body returned')

    def test_process_body_error(self):
        """
        process body must throw an error if expected fields are not in body
        """
        request = HttpRequest()
        expected = ['field_that_body_does_not_contain']
        body = {'only_body_field': "value"}
        request._body = json.dumps(body)
        json_mixin = JsonMixin()
        with self.assertRaises(Exception):
            json_mixin.process_body(request, expected)

    def test_render_to_json_response(self):
        """
        render_to_json response must combine JsonResponse object
        """
        response_data = {'key': 'value'}
        status = 418
        expected_body = JsonResponse(response_data, status=status)
        json_mixin = JsonMixin()
        self.assertEqual(expected_body.__dict__,
                         json_mixin.render_to_json_response(response_data,
                                                            status=status).__dict__)

    def test_respond_error_json(self):
        """
        respond_error_json response must combine JsonResponse object
        """
        status = 418
        error = 'error'
        expected_body = JsonResponse({
            'status': 'error',
            'message': error
        }, status=status)
        json_mixin = JsonMixin()
        self.assertEqual(expected_body.__dict__,
                         json_mixin.respond_error_json(error,
                                                       status=status).__dict__)

    def test_respond_success_json(self):
        """
        respond_success_json response must combine JsonResponse object
        """
        status = 418
        response_data = {'key': 'value'}
        expected_body = JsonResponse({
            'key': 'value',
            'status': 'ok'
        }, status=status)
        json_mixin = JsonMixin()
        self.assertEqual(expected_body.__dict__,
                         json_mixin.respond_success_json(response_data,
                                                         status=status).__dict__)

