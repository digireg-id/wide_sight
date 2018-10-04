import sys
from uuid import UUID

from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIAccess
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_gis.filters import DistanceToPointFilter
from rest_framework.exceptions import APIException
from rest_condition import Or

from .models import sequences, panoramas, image_object_types, image_objects, userkeys, appkeys
from .serializers import panoramas_geo_serializer, sequences_serializer, panoramas_serializer, image_object_types_serializer, image_objects_serializer, userkeys_serializer
from .permissions import baseAPIPermission

class sequencesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows to be view or edit sequences of panorama images.

    get:
    Return a list of all the existing sequences.

    post:
    Create a new sequence instance.

    patch:
    edit and update an existing sequence.

    delete:
    permanently delete an existing empty sequence.
    """
    queryset = sequences.objects.all()
    serializer_class = sequences_serializer
    permission_classes = ( Or(baseAPIPermission, IsAuthenticated, HasAPIAccess),)
    filter_backends = (DjangoFilterBackend,)

class panoramasViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = panoramas.objects.all()
    serializer_class = panoramas_serializer
    permission_classes = ( Or(baseAPIPermission, IsAuthenticated, HasAPIAccess),)
    distance_filter_field = 'geom'
    filter_backends = (DjangoFilterBackend, DistanceToPointFilter, )
    filterset_fields = ('sequence', 'id', )


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        print ("instance",instance, file=sys.stderr)
        print ("args",instance, file=sys.stderr)
        print ("kwargs",instance, file=sys.stderr)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


    def get_queryset(self):
        #print ("get_filterset",self, dir(self), file=sys.stderr)
        limit = self.request.query_params.get('limit', None)
        userkey = self.request.query_params.get('userkey', None)
        as_geojson = self.request.query_params.get('as_geojson', None)

        if userkey:
            try:
                uuidkey = UUID(userkey)
            except:
                raise APIException('bad userkey')
            if userkeys.objects.filter(pk=uuidkey).exists():
                self.queryset = self.queryset.filter(sequence__creator=uuidkey)
            else:
                raise APIException('userkey not found')

        if as_geojson:
            self.serializer_class = panoramas_geo_serializer

        if not limit:
            limit = 10 #set default limit parameter
        elif limit > 500: #set default limit parameter
            limit = 500 #set default limit parameter
        return self.queryset[:limit]


class image_object_typesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = image_object_types.objects.all()
    serializer_class = image_object_types_serializer
    permission_classes = ( Or(baseAPIPermission, IsAuthenticated, HasAPIAccess),)


class image_objectsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = image_objects.objects.all()
    serializer_class = image_objects_serializer
    permission_classes = ( Or(baseAPIPermission, IsAuthenticated, HasAPIAccess),)


class userkeysViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = userkeys.objects.all()
    serializer_class = userkeys_serializer
    permission_classes = ( Or(baseAPIPermission, IsAuthenticated, HasAPIAccess),)
