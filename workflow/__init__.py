VERSION = (1, '5rc1')

def get_version():
    return '.'.join([str(i) for i in VERSION])

__version__ = get_version()

default_app_config = 'workflow.apps.WorkflowConfig'
