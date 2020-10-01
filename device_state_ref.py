device_state_info = [
    {
        'unique_id': 'x001',
        'states': [
            {
                'component': 'main',
                'capability': 'st.switch',
                'attribute': 'switch',
                'value': 'on'
            },
            {
                'component': 'main',
                'capability': 'st.switchLevel',
                'attribute': 'level',
                'value': 50
            }
        ]
    },
    {
        'unique_id': 'x002',
        'states': [
            {
                'component': 'main',
                'capability': 'st.switch',
                'attribute': 'switch',
                'value': 'on'
            },
            {
                'component': 'main',
                'capability': 'st.healthCheck',
                'attribute': 'healthStatus',
                'value': 'online'
            },
            {
                'component': 'main',
                'capability': 'st.thermostatMode',
                'attribute': 'thermostatMode',
                'value': 'auto'
            },
            {
                'component': 'main',
                'capability': 'st.thermostatCoolingSetpoint',
                'attribute': 'coolingSetpoint',
                'value': 16,
                'unit': 'C'
            }
        ]
    },
    {
        'unique_id': 'x003',
        'states': [
            {
                'component': 'main',
                'capability': 'st.healthCheck',
                'attribute': 'healthStatus',
                'value': 'online'
            },
            {
                'component': 'main',
                'capability': 'st.thermostatCoolingSetpoint',
                'attribute': 'coolingSetpoint',
                'value': 16,
                'unit': 'C'
            },
            {
                'component': 'main',
                'capability': 'st.thermostatHeatingSetpoint',
                'attribute': 'heatingSetpoint',
                'value': 23,
                'unit': 'C'
            }
        ]
    },
    {
        'unique_id': 'x004',
        'states': [
            {
                'component': 'main',
                'capability': 'st.healthCheck',
                'attribute': 'healthStatus',
                'value': 'online'
            },
            {
                'component': 'main',
                'capability': 'st.doorControl',
                'attribute': 'door',
                'value': 'open',
            }
        ]
    },
    {
        'unique_id': 'x005',
        'states': [
            {
                'component': 'main',
                'capability': 'st.windowShade',
                'attribute': 'windowShade',
                'value': 'open'
            },
            {
                'component': 'main',
                'capability': 'st.supportedWindowShadeCommands',
                'attribute': 'windowShade',
                'value': [
                    'open',
                    'close'
                ]
            },
            {
                'component': 'main',
                'capability': 'st.switch',
                'attribute': 'switch',
                'value': 'on',
            },
            {
                'component': 'main',
                'capability': 'st.switchLevel',
                'attribute': 'level',
                'value': 50
            }
        ]
    },
    {
        'unique_id': 'x006',
        'states': [
            {
                'component': 'main',
                'capability': 'st.valve',
                'attribute': 'valve',
                'value': 'open'
            },
            {
                'component': 'main',
                'capability': 'st.healthCheck',
                'attribute': 'healthStatus',
                'value': 'online',
            }
        ]
    }
]
import pickle
basedir = '/home/bts/Documents/Projects/ST-Schema-Pyhton-SDK/ST-Schema-Python-Samples/simple-python-schema-connector/lib/webhook/data/device_state_info.p'
with open(basedir, 'wb') as info:
    pickle.dump(device_state_info, info)