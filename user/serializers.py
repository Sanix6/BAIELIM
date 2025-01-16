from category.serializers import CostTypeSerializer, RegionSerializer
from user import models, utils
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class AdminSerializer(serializers.ModelSerializer):
    """Serializer for user"""

    class Meta:
        model = models.ModelAdmin
        fields = ('id', 'name', 'login', 'password', 'user_type')
        extra_kwargs = {
            'password': {'write_only': True}
        }
        # read_only_fields = ('user_type', )

    def create(self, validated_data):
        """Create user with encrypted password and return it"""
        administrator = models.ModelAdmin.objects.create_user(**validated_data)
        administrator.set_password(validated_data['password'])
        administrator.user_type = utils.ADMINISTRATOR
        administrator.save()
        return administrator


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Manager
        fields = ('id', 'name', 'login', 'password', 'user_type')
        extra_kwargs = {
            'password': {'write_only': True}
        }
        # read_only_fields = ('user_type', )

    def create(self, validated_data):
        """Create user with encrypted password and return it"""
        manager = models.Manager.objects.create_user(**validated_data)
        manager.set_password(validated_data['password'])
        manager.user_type = utils.MANAGER
        manager.save()
        return manager


class AgentSerializer(serializers.ModelSerializer):
    """Serializer for stores"""

    class Meta:
        model = models.Agent
        fields = ('id', 'name', 'login', 'password', 'passport_front', 'passport_back', 'birthdate', 'address',
                  'phoneNumber', 'user_type', 'balance', 'costTypes', 'photo', 'oneC_code', 'is_active')
        extra_kwargs = {
            'password': {'write_only': True}
        }
        # read_only_fields = ('user_type', )

    def create(self, validated_data):
        """Create user with encrypted password and return it"""
        costTypes = validated_data.pop('costTypes', None)
        agent = models.Agent.objects.create_user(**validated_data)
        agent.set_password(validated_data['password'])
        agent.user_type = utils.AGENT
        agent.save()
        agent.costTypes.set(costTypes)
        agent.save()
        return agent


class AgentSerializerGet(serializers.ModelSerializer):
    """Serializer for stores"""
    costTypes = CostTypeSerializer(many=True)

    class Meta:
        model = models.Agent
        fields = ('id', 'name', 'login', 'password', 'passport_front', 'passport_back', 'birthdate', 'address',
                  'phoneNumber', 'user_type', 'balance', 'costTypes', 'photo', 'oneC_code', 'is_active')
        extra_kwargs = {
            'password': {'write_only': True}
        }
        read_only_fields = ('user_type', )


class AgentSerializerOneC(serializers.ModelSerializer):
    class Meta:
        model = models.Agent
        fields = ('name', )


class AgentSerializerOpen(serializers.ModelSerializer):
    class Meta:
        model = models.Agent
        fields = ('id', 'name', 'oneC_code',)


class StoreSerializer(serializers.ModelSerializer):
    """Serializer for regular account"""

    class Meta:
        model = models.Store
        fields = ('id', 'name', 'login', 'password', 'contactName', 'photo', 'phoneNumber', 'phoneNumber1',
                  'phoneNumber2', 'phoneNumber3', 'score', 'address', 'lat', 'lon', 'costType', 'user_type',
                  'dateCreated', 'area', 'documents', 'oneC_code', 'is_active', 'store_agent', 'region')

        extra_kwargs = {'password': {'write_only': True}, }
        # read_only_fields = ('user_type', )

    def create(self, validated_data):
        """Create user with encrypted password and return it"""
        store = models.Store.objects.create_user(**validated_data)
        store.set_password(validated_data['password'])
        store.user_type = utils.STORE
        store.save()
        return store


class StoreSerializerGet(serializers.ModelSerializer):
    """Serializer for regular account"""
    costType = CostTypeSerializer()
    store_agent = AgentSerializer()
    region = RegionSerializer()

    class Meta:
        model = models.Store
        fields = ('id', 'name', 'login', 'password', 'contactName', 'photo', 'phoneNumber', 'phoneNumber1',
                  'phoneNumber2', 'phoneNumber3', 'score', 'address', 'lat', 'lon', 'costType', 'user_type',
                  'dateCreated', 'area', 'documents', 'oneC_code', 'is_active', 'store_agent', 'region', 'guid')

        extra_kwargs = {'password': {'write_only': True}, }
        read_only_fields = ('user_type', )


class StoreSerializerOpen(serializers.ModelSerializer):
    class Meta:
        model = models.Store
        fields = ('id', 'name')


class StoreSerializerForGet(serializers.ModelSerializer):
    class Meta:
        model = models.Store
        fields = ('id', 'name', 'lat', 'lon')


class StoreSerializerJune(serializers.ModelSerializer):
    class Meta:
        model = models.Store
        fields = ('id', 'name', 'oneC_code', 'address')
        
        
class StoreSerializerForOrder(serializers.ModelSerializer):
    class Meta:
        model = models.Store
        fields = ('id', 'name', 'login', 'contactName', 'photo', 'phoneNumber', 'score', 'address', 'lat',
                  'lon', 'costType',)


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Driver
        fields = ('id', 'name', 'login', 'password', 'photo', 'passport_front', 'passport_back', 'phoneNumber',
                  'balance', 'user_type', 'oneC_code', 'is_active')
        extra_kwargs = {'password': {'write_only': True}, }
        # read_only_fields = ('user_type', )

    def create(self, validated_data):
        """Create user with encrypted password and return it"""
        driver = models.Driver.objects.create_user(**validated_data)
        driver.set_password(validated_data['password'])
        driver.user_type = utils.DRIVER
        driver.save()
        return driver


class DriverSerializerOpen(serializers.ModelSerializer):
    class Meta:
        model = models.Driver
        fields = ('id', 'name')


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['user_type'] = user.user_type
        token['is_active'] = user.is_active
        # ...

        return token


class PlanStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PlanStore
        fields = ('id', 'store', 'status', 'photo', 'comment', 'madeOrder')


class PlanStoreSerializerGet(serializers.ModelSerializer):
    store = StoreSerializerGet()

    class Meta:
        model = models.PlanStore
        fields = ('id', 'store', 'status', 'photo', 'comment', 'madeOrder')


class DayPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DayPlan
        fields = ('id', 'day', 'agent', 'status', 'stores_plan', 'driver', 'dateCreated', 'dateVisit')


class DayPlanSerializerGet(serializers.ModelSerializer):
    agent = AgentSerializer()
    stores_plan = PlanStoreSerializerGet(many=True)
    driver = DriverSerializer()

    class Meta:
        model = models.DayPlan
        fields = ('id', 'day', 'agent', 'status', 'stores_plan', 'driver', 'dateCreated', 'dateVisit')


class OneCStoreSerializer(serializers.ModelSerializer):
    Guid = serializers.SerializerMethodField()
    Код = serializers.CharField(source='oneC_code')
    Наименование = serializers.SerializerMethodField()
    Комментарий = serializers.SerializerMethodField()

    class Meta:
        model = models.Store
        fields = ['Guid', 'Код', 'Наименование', 'Комментарий']

    def get_Наименование(self, obj):
        return f"{obj.name}, {obj.address}, {obj.phoneNumber}"

    def get_Комментарий(self, obj):
        return obj.store_agent.name if obj.store_agent else ''

    def get_Guid(self, obj):
        if len(obj.guid) == 0:
            guid = '00000000-0000-0000-0000-'
            txt = str(obj.id).zfill(12)
            guid = guid + txt
        else:
            guid = obj.guid
        return guid


class ChangePasswordWithoutOldPassowrdSerializer(serializers.Serializer):
    models = User

    new_password = serializers.CharField(required=True)
    user_id = serializers.CharField(required=True)
