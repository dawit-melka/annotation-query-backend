import pytest
import json
import logging
from app import app
import os
import yaml

# Disable logging for cleaner test output
logging.getLogger('neo4j').setLevel(logging.CRITICAL)

@pytest.fixture
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '../../..', 'config', 'config.yaml')
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        logging.info("Configuration loaded successfully.")
        return config
    except FileNotFoundError:
        logging.error(f"Config file not found at: {config_path}")
        raise
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML file: {e}")
        raise

@pytest.fixture
def setup_database():
    """Fixture to configure the database type dynamically using load_config."""
    # Load the configuration and set the database type
    config = load_config()
    config['database']['type'] = 'cypher'
    
    # Ensure the config change is applied
    yield config

def test_process_query(query_list, schema):
    # make a call to the /query endpoint

    with app.test_client() as client:
        response = client.post('/query', data=json.dumps(query_list), content_type='application/json')
        assert response._status == '200 OK'

        # test output dict keys
        response_json = response.get_json()
        assert tuple(response_json.keys()) == ('nodes', "edges")

        # test the nodes response value is a list
        assert isinstance(response_json['nodes'], list) == True
        assert isinstance(response_json['edges'], list) == True

        assert len(response_json['nodes']) != 0

        i = 0
        # check the schema of the first 10 nodes responses
        while i < len(response_json['nodes']) and i < 10:
            value = response_json['nodes'][i]
            assert isinstance(value, dict)
            keys = list(schema[value['data']['type']]['properties'].keys())
            keys.append('id')
            keys.append('type')
            if 'synonyms' in keys:
                keys.remove('synonyms')
            assert keys.sort() == list(value['data'].keys()).sort()
            i += 1

        i = 0
        while i < len(response_json['edges']) and i < 10:
            value = response_json['edges'][i]
            assert isinstance(value, dict)
            keys = ["label", "source", "target", "source_data", "source_url"]
            assert keys.sort() == list(value['data'].keys()).sort()
            i += 1
