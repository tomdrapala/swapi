from datetime import datetime
from logging import getLogger

from rest_framework import serializers

from people.models import Character, People

logger = getLogger(__name__)
EMPTY_VALUE = ['unknown', 'n/a', 'none']


class PeopleSerializer(serializers.ModelSerializer):
    class Meta:
        model = People
        exclude = ('is_removed',)

    def parse_date(self, date):
        for fmt in ('%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ'):
            try:
                return datetime.strptime(date, fmt).strftime("%d %B %Y, %H:%M:%S")
            except ValueError:
                # In case of parsing failure just return the raw date string
                pass
        return date

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['date_created'] = self.parse_date(ret['date_created'])
        return ret


class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        exclude = ()

    def format_date(self, value):
        try:
            return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ').date()
        except ValueError as e:
            logger.error(f"Error while parsing date - {e}")
            raise serializers.ValidationError

    def empty_value_validation(self, value):
        if value in EMPTY_VALUE:
            return None
        return value

    def empty_value_list_validation(self, value):
        if value[0] in EMPTY_VALUE and len(value) == 1:
            return None
        return value

    def validate_skin_color(self, value):
        return self.empty_value_list_validation(value)

    def validate_eye_color(self, value):
        return self.empty_value_list_validation(value)

    def validate_hair_color(self, value):
        return self.empty_value_list_validation(value)

    def validate_birth_year(self, value):
        return self.empty_value_validation(value)

    def validate_gender(self, value):
        return self.empty_value_validation(value)

    def validate_homeworld(self, value):
        return self.empty_value_validation(value)

    def to_internal_value(self, data):
        if data.get('edited'):
            data['date'] = self.format_date(data.pop('edited'))
        if data.get('height') in EMPTY_VALUE:
            data['height'] = None
        if data.get('mass') in EMPTY_VALUE:
            data['mass'] = None
        elif data.get('mass'):
            data['mass'] = data['mass'].replace(',', '').replace('.', '')
        if data.get('birth_year'):
            data['birth_year'] = data['birth_year'].replace(',', '').replace('.', '')
        if data.get('skin_color'):
            data['skin_color'] = data['skin_color'].split(',')
        if data.get('eye_color'):
            data['eye_color'] = data['eye_color'].split(',')
        if data.get('hair_color'):
            data['hair_color'] = data['hair_color'].split(',')
        return super().to_internal_value(data)
