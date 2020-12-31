from rest_framework import serializers

from deal.models import Deal, Users, Gem


class FileUploadSerializer(serializers.Serializer):
    deals = serializers.FileField()

    class Meta:
        fields = ['deals', ]


class UsersSerializer(serializers.ModelSerializer):
    customer = serializers.CharField(source='username')

    class Meta:
        model = Users
        fields = ['customer']


class GemSerializer(serializers.ModelSerializer):
    item = serializers.CharField(source='title')

    class Meta:
        model = Gem
        fields = ['item']


class DealSerializer(serializers.ModelSerializer):
    customer = serializers.CharField(source='customer.username')
    item = serializers.CharField(source='item.title')

    class Meta:
        model = Deal
        fields = ['customer', 'item', 'total', 'quantity', 'date']