import urllib2
from urllib2 import HTTPError
import base64
import logging
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template import Context, loader, Template
from django.utils import simplejson as json
from django.utils import html
from django.forms.models import model_to_dict
from geonode.maps.models import Map
from geonode.layers.models import Layer
from geonode.printing.models import PrintTemplate
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


def printing_print(request, templateid, resource_context, format):
    """Interpolate the template with the given id"""
    try:

        # get the template from the django database
        template = get_template(templateid)
        # Apply the vars to the template and render it
        rendered = render_template(request, template, resource_context)
        # build to url to be sent to GeoServer
        url = "%sjson?format=%s" % (settings.GEOSERVER_PRINT_URL, format)

        ## add the auth headers to urllib2
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(
            None,
            "geoserver",
            settings.GEOSERVER_CREDENTIALS[0],
            settings.GEOSERVER_CREDENTIALS[1]
        )

        urllib2.install_opener(urllib2.build_opener(
            urllib2.HTTPBasicAuthHandler(passman)
        ))

        print_req = urllib2.Request(url, rendered)
        ### FIXME, This code should use the urllib2 password manager
        base64string = base64.encodestring(
            '%s:%s' % (settings.GEOSERVER_CREDENTIALS[0],
                       settings.GEOSERVER_CREDENTIALS[0])).replace('\n', '')
        print_req.add_header("Authorization", "Basic %s" % base64string)

        ### add the correct content type to the request
        print_req.add_header('Content-Type', 'text/html')
        printed = urllib2.urlopen(print_req)
    except HTTPError, e:
        return HttpResponse(
            e.reason,
            mimetype="text/plain",
            status=500
        )
    return HttpResponse(printed, content_type="application/json")


def get_resource_context(mapid=None, layerid=None):
    if mapid is not None:
        resource_obj = get_object_or_404(Map, pk=mapid)
    else:
        resource_obj = get_object_or_404(Layer, typename=layerid)
    return resource_obj


@csrf_exempt
def printing_print_map(request, templateid, mapid=None):
    resource_context = get_resource_context(mapid=mapid)
    return printing_print(request, templateid, resource_context, 'pdf')


@csrf_exempt
def printing_print_layer(request, templateid, layerid=None):
    resource_context = get_resource_context(layerid=layerid)
    return printing_print(request, templateid, resource_context, 'pdf')


@csrf_exempt
def printing_preview_map(request, templateid, mapid=None):
    resource_context = get_resource_context(mapid=mapid)
    return printing_print(request, templateid, resource_context, 'png')


@csrf_exempt
def printing_preview_layer(request, templateid, layerid=None):
    resource_context = get_resource_context(layerid=layerid)
    return printing_print(request, templateid, resource_context, 'png')


def get_template(templateid):
    template_obj = get_object_or_404(PrintTemplate, pk=templateid)
    if template_obj.contents:
        template = Template(template_obj.contents)
    else:
        if not template_obj.url.find("http", 0, 4) > -1:
            template = loader.get_template(template_obj.url)
        else:
            remote_template = urllib2.urlopen(template_obj.url)
            template = Template(remote_template.readlines())
    return template


def render_template(request, template, resource_context):
    render_data = request.POST.copy()
    render_data.update(model_to_dict(resource_context))
    context = Context(render_data)
    rendered = template.render(context)
    return rendered


#require_GET()
def printing_template_list(request):
    """list the available templates"""
    templates = []
    for t in PrintTemplate.objects.all():
        data = model_to_dict(t)
        data['contents'] = html.escape(data.get('contents', ''))
        data.update({"id": t.pk})
        templates.append(data)
    return HttpResponse(
        json.dumps(templates),
        mimetype="application/json"
    )
