from django.conf import settings
from django.http import HttpResponse, Http404
from django.utils import simplejson as json
from django.views.generic import View
from rapidsms.models import Backend, Connection

UREPORT_JSON_API_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


class UReporterApiView(View):
    def parse_url_parameters(self, kwargs):
        self.backend_name = kwargs.get("backend")
        self.user_address = kwargs.get("user_address")
        if kwargs.get("poll_id"):
            self.poll_id = kwargs.get("poll_id")

    def get_backend(self):
        backend = Backend.objects.get(name=self.backend_name)
        return backend

    def get_connection(self):
        connection, connection_created = Connection.objects.get_or_create(identity=self.user_address,
                                                                              backend=self.backend)
        return connection


    def create_json_response(self, response_data, status_code=200):
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=status_code)

    def get(self, request, *args, **kwargs):
        raise NotImplementedError("Define in subclass")

    def post(self, request, *args, **kwargs):
        raise NotImplementedError("Define in subclass")

    def contact_exists(self, connection):
        return connection is not None and connection.contact is not None

    def get_datetime_format(self):
        return getattr(settings, "UREPORT_JSON_API_DATETIME_FORMAT", UREPORT_JSON_API_DATETIME_FORMAT)

    def dispatch(self, request, *args, **kwargs):
        self.parse_url_parameters(kwargs)
        try:
            self.backend = self.get_backend()
        except Backend.DoesNotExist:
            raise Http404()
        self.connection = self.get_connection()
        return super(UReporterApiView, self).dispatch(request, *args, **kwargs)

