from dtrlb import DTRLB

def get_config(path) -> dict:
    with open(path, 'r') as f:
        import json
        conf = json.load(f)
        return conf
config = get_config('work/config.json')

bot = DTRLB(
    token=config['token']
)
bot.setup_logging()

bot.launch()