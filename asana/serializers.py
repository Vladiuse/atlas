from rest_framework import serializers

from .models import AsanaWebhookRequestData


class AsanaWebhookRequestDataSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AsanaWebhookRequestData
        exclude = ("headers", )
