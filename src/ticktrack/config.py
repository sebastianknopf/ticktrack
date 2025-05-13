class Configuration:

    @classmethod
    def default_config(cls, config):
        # some of the default config keys are commented in order to force
        # the user to provide these configurations actively
        
        default_config = {
            'app': {
                #'endpoint': 'https://efa.app/trias',
                #'api_key': 'AwesomeApiKey',
                'datalog_enabled': False
            },
            'stations': [],
            'lines': []
        }

        return cls._merge_config(default_config, config)
    
    @classmethod
    def _merge_config(cls, defaults: dict, actual: dict) -> dict:
        if isinstance(defaults, dict) and isinstance(actual, dict):
            return {k: cls._merge_config(defaults.get(k, {}), actual.get(k, {})) for k in set(defaults) | set(actual)}
        
        return actual if actual else defaults