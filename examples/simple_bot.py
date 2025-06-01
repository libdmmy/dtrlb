from dtrlb import DTRLB
from dtrlb.plugins import EchoPlugin, CalcPlugin

bot = DTRLB(
    plugins=[EchoPlugin(), CalcPlugin()],
)

bot.launch()