import json
from collections import defaultdict
from logging import getLogger

import requests
from django.conf import settings
from rest_framework import status

from people.serializers import CharacterSerializer

logger = getLogger(__name__)
PEOPLE_URL = getattr(settings, 'PEOPLE_URL', '')
HOMEWORLD_URL = getattr(settings, 'HOMEWORLD_URL', '')


def fetch_data(url):
    result = requests.get(url)
    if getattr(result, 'status_code', 0) == status.HTTP_200_OK:
        try:
            return json.loads(result.content)
        except json.JSONDecodeError:
            logger.error(f"Error while fetching SW data - {result}")
            pass
    return dict()


def get_resource_data(url):
    data = list()
    chunk = fetch_data(url)
    data.extend(chunk.get('results', []))
    while chunk.get('next'):
        chunk = fetch_data(chunk['next'])
        data.extend(chunk.get('results'))
    return data


def get_homeworld_mapping(homeworld_data):
    homeworld_data = get_resource_data(HOMEWORLD_URL)
    mapping = defaultdict(str)
    for obj in homeworld_data:
        planet_id = obj['url'].split('/')[-2]
        mapping[planet_id] = obj['name']
    return mapping


def substitute_homeworld_names(data):
    homeworlds = {obj.get('homeworld') for obj in data}
    homeworld_mapping = get_homeworld_mapping(homeworlds)
    for obj in data:
        planet_id = obj['homeworld'].split('/')[-2]
        obj['homeworld'] = homeworld_mapping[planet_id]
    return data


def fetch_people_data():
    data = get_resource_data(PEOPLE_URL)
    data = substitute_homeworld_names(data)
    if data:
        serializer = CharacterSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data
