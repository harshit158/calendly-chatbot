'''This module contains tool definitions for OpenAI API Function Calling'''

tools = [
    {
        "type": "function",
        "function":
            {
            'name': 'list_events',
            'description': 'Call list_events endpoint of calendly',
            'parameters': {
                'type': 'object',
                'properties': {
                    'count': {
                        'type': 'integer',
                        'description': 'Number of events to return. '
                    },
                    'invitee_email': {
                        'type': 'string',
                        'description': 'The email address of the invitee'
                    },
                    'max_start_time': {
                        'type': 'string',
                        'description': 'The upper range of start time in the example format: 2020-01-02T12:30:00:000000Z'
                    },
                    'min_start_time': {
                        'type': 'string',
                        'description': 'The lower range of start time in the example format: 2020-01-02T12:30:00:000000Z'
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function":
            {
            'name': 'cancel_event',
            'description': 'Cancel an event from calendly',
            'parameters': {
                'type': 'object',
                'properties': {
                    'uuid': {
                        'type': 'string',
                        'description': 'URI of the event to cancel. Example format: 5ad394e1-e969-4ab8-b661-e0077f1b476c'
                    },
                    'reason': {
                        'type': 'string',
                        'description': 'Reason for cancellation'
                    },
                }, 
                'required': ['uuid']
            }
        }
    },
]