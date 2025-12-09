from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class TokenOnlySerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        return {"token": data["access"]}

class TokenOnlyView(TokenObtainPairView):
    serializer_class = TokenOnlySerializer
