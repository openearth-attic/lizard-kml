from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponse
from django.utils import simplejson as json
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.decorators.cache import never_cache

from lizard_kml.models import Category

class JsonView(View):
    '''
    Simple view which serializes the data returned by an overridden
    method ``get_json`` to JSON.
    '''
    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        data = self.get_json(request, *args, **kwargs)
        if isinstance(data, HttpResponse):
            return data
        else:
            serialized_data = json.dumps(data)
            return HttpResponse(serialized_data, content_type='application/json')

class CategoryTreeView(JsonView):
    '''
    As consumed by Ext JS. Returns a tree structure with categories
    and KML resources as leaf nodes.
    '''
    def get_json(self, request):
        categories = [
            {
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'collapsed_by_default': category.collapsed_by_default,
                'kml_resources': self._kml_resource_tree(category)
            }
            for category in Category.objects.all()
        ]
        return {'categories': categories}

    def _kml_resource_tree(self, category):
        return [
            {
                'id': k.id,
                'name': k.name,
                'description': k.description,
                'kml_type': k.kml_type,
                'kml_url': self._mk_kml_resource_url(k),
                'slug': k.slug,
                'preview_image_url': k.preview_image.url if k.preview_image else ''
            }
            for k in category.kmlresource_set.all()
        ]

    def _mk_kml_resource_url(self, kml_resource):
        if kml_resource.slug == 'jarkus':
            rela = reverse('lizard-jarkus-kml', kwargs={'kml_type': 'lod'})
        else:
            ext = 'kmz' if kml_resource.url.lower().endswith('kmz') else 'kml'
            rela = reverse('lizard-kml-kml', kwargs={'kml_resource_id': kml_resource.pk, 'ext': ext})
        absurl = self.request.build_absolute_uri(rela)
        return absurl
