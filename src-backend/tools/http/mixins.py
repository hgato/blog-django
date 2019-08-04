import json
from django.http import JsonResponse


class JsonMixin:
    def clean_body(self, request):
        return json.loads(request.body)

    def check_body(self, body: dict, expected_parameters: list):
        error_list = []
        for parameter in expected_parameters:
            if parameter not in body:
                error_list.append(parameter)
        if error_list:
            raise Exception('Request demands following parameters: ' + ', '.join(error_list))

    def process_body(self, request, expected_parameters=None):
        body = self.clean_body(request)
        if expected_parameters:
            self.check_body(body, expected_parameters)
        return body

    def render_to_json_response(self, context, **response_kwargs):
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        return context

    def respond_error_json(self, error, status=400):
        response = {
            'status': 'error',
            'message': str(error),
        }
        return self.render_to_json_response(response, status=status)

    def respond_success_json(self, payload=None):
        if not payload:
            payload = {}
        payload['status'] = 'ok'
        return self.render_to_json_response(payload)
