from dtrlb import DTRLB
from dtrlb.plugins import EchoPlugin, CalcPlugin, EventLogPlugin, SecurityPlugin

bot = DTRLB(
    plugins=[EchoPlugin(), CalcPlugin(), EventLogPlugin(), 
             SecurityPlugin(trusted_users=[])],
)

bot.launch()