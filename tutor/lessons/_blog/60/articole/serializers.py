from rest_framework import serializers

from .models import Articol


class ArticolSerializer(serializers.ModelSerializer):
    """Cum arată un articol în JSON: câmpurile alese și cum se transformă."""

    autor = serializers.ReadOnlyField(source="autor.username")
    categorie = serializers.StringRelatedField()

    class Meta:
        model = Articol
        fields = ["id", "titlu", "continut", "data_publicarii", "categorie", "autor"]
