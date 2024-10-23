import pytz
from django.utils.timezone import get_current_timezone
from rest_framework import serializers
from apps.console.account.models import CoreAccount
from apps.console.api.v1.utils.api_helpers import CurrentAccountDefault, CurrentMemberDefault
from apps.console.connection.models import CoreConnection, CoreIntegration, CoreConnectionLocation
from apps.console.node.models import CoreDigitalOcean, CoreNode, CoreSchedule
from apps.console.utils.models import UtilBackup
from apps.console.api.v1.node.serializers import CoreNodeReadSerializer, CoreCloudNodeWriteSerializer


class CoreCloudDigitalOceanReadSerializer(serializers.ModelSerializer):
    node = CoreNodeReadSerializer(read_only=True)
    totals = serializers.SerializerMethodField()

    class Meta:
        model = CoreDigitalOcean
        fields = "__all__"
        datatables_always_serialize = ("id", "unique_id", "notes")

    @staticmethod
    def get_totals(obj):
        totals = {
            "backups": obj.backups.filter(status=UtilBackup.Status.COMPLETE).count(),
            "schedules": CoreSchedule.objects.filter(node=obj.node, status=CoreSchedule.Status.ACTIVE).count(),
        }
        return totals


class CoreCloudDigitalOceanWriteSerializer(serializers.ModelSerializer):
    node = CoreCloudNodeWriteSerializer(write_only=True)

    class Meta:
        model = CoreDigitalOcean
        fields = "__all__"

    def create(self, validated_data):
        node = validated_data.pop("node", [])
        validated_data["node"] = CoreNode.objects.create(**node)
        instance = CoreDigitalOcean.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        node = validated_data.pop("node", [])
        super().update(instance.node, node)
        instance = super().update(instance, validated_data)
        return instance