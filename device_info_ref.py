
device_info = [
    {
        'unique_id': 'x001',
        'label': 'switch_example',
        'device_handler': 'c2c-dimmer',
        'device_type': 'Dimmer Switch',
        'mn': {
            'mn': 'mock manufacturer',
            'model': '0.0.1',
            'hw_version': '0.0.1',
            'sw_version': '0.0.1'
        },
        'context': {
            'room_name': 'default',
            'groups': ['example_device'],
            'categories': ['switch']
        }
    },
    {
        'unique_id': 'x002',
        'label': 'air_conditioner_example',
        'device_handler': '577c8d5e-8cc9-4c4b-b3d5-cd8c1f632697',
        'device_type': 'Air Conditioner',
        'mn': {
            'mn': 'mock manufacturer',
            'model': '0.0.1',
            'hw_version': '0.0.1',
            'sw_version': '0.0.1'
        },
        'context': {
            'room_name': 'default',
            'groups': ['example_device'],
            'categories': ['air-conditioner']
        }
    },
    {
        'unique_id': 'x003',
        'label': 'thermostat_example',
        'device_handler': 'fe75655a-b1e2-475c-8878-d0f3882bf14b',
        'device_type': 'Thermostat',
        'mn': {
            'mn': 'mock manufacturer',
            'model': '0.0.1',
            'hw_version': '0.0.1',
            'sw_version': '0.0.1'
        },
        'context': {
            'room_name': 'default',
            'groups': ['example_device'],
            'categories': ['thermostat']
        }
    },
    {
        'unique_id': 'x004',
        'label': 'garage_door_example',
        'device_handler': 'a69361c5-c13c-47c4-bf16-29c967c80feb',
        'device_type': 'Garage Door',
        'mn': {
            'mn': 'mock manufacturer',
            'model': '0.0.1',
            'hw_version': '0.0.1',
            'sw_version': '0.0.1'
        },
        'context': {
            'room_name': 'default',
            'groups': ['example_device'],
            'categories': ['garage-door']
        }
    },
    {
        'unique_id': 'x005',
        'label': 'window_shade_example',
        'device_type': '38ce7e04-ab18-4680-a866-d59e63c50ef2',
        'device_handler': 'Window Shade',
        'mn': {
            'mn': 'mock manufacturer',
            'model': '0.0.1',
            'hw_version': '0.0.1',
            'sw_version': '0.0.1'
        },
        'context': {
            'room_name': 'default',
            'groups': ['example_device'],
            'categories': ['blind']
        }
    },
    {
        'unique_id': 'x006',
        'label': 'valve_example',
        'device_handler': '7faaccf1-304b-45e9-8e81-e1b1470c4b73',
        'device_type': 'Valve',
        'mn': {
            'mn': 'mock manufacturer',
            'model': '0.0.1',
            'hw_version': '0.0.1',
            'sw_version': '0.0.1'
        },
        'context': {
            'room_name': 'default',
            'groups': ['example_device'],
            'categories': ['water-valve']
        }
    }
]
import pickle
basedir = '/home/bts/Documents/Projects/ST-Schema-Pyhton-SDK/ST-Schema-Python-Samples/simple-python-schema-connector/lib/webhook/data/device_info.p'
with open(basedir, 'wb') as info:
    pickle.dump(device_info, info)

