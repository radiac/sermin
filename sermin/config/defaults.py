"""
Default core Sermin settings
"""
from ..constants import VERBOSITY_DEBUG
from .module import settings, Setting


settings.sermin = 'Sermin'
settings.sermin.dryrun = Setting('Dry run', default=False)
settings.sermin.confirm = Setting('Confirm actions', default=False)
settings.sermin.verbosity = Setting(
    'Reporting verbosity', default=VERBOSITY_DEBUG,
)

settings.sermin.source = Setting('Source of the blueprint')
settings.sermin.host = Setting('Host to apply the blueprint to', list=True)
