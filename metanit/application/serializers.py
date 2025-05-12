from rest_framework import serializers
from .models import Content, TypeContent, Creator, ReasonsToBuy


class TypeContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeContent
        fields = ["title_type"]


class CreatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Creator
        fields = ["name", "summery"]


class ReasonsToBuySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReasonsToBuy
        fields = ["summery"]


class ContentSerializer(serializers.ModelSerializer):
    creator = CreatorSerializer(many=True)
    reasons_to_buy = ReasonsToBuySerializer(many=True)
    type_content = TypeContentSerializer()

    class Meta:
        model = Content
        fields = "__all__"
