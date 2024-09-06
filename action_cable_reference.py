import aioactioncable
import asyncio
import json
import ssl

state = {}
def process(msg):
  msg_json = json.loads(msg)
  print(f'Processing {msg_json}')
  # JSON is in this format: {'experiment': 4, 'control': 'dial_2', 'value': '54', 'controlId': 0.73771245889517, 'location': 'pi'}
  state[msg_json['control']] = msg_json['value']

      
    


async def ac_recv(uri, identifier):
  async with aioactioncable.connect(uri) as acconnect:
    subscription = await acconnect.subscribe(identifier)
    async for msg in subscription:
      if json.loads(msg)['location'] == 'pi':
        process(msg)
        await subscription.send({**json.loads(msg), 'location': 'controls'})

asyncio.run(ac_recv('ws://127.0.0.1:3000/cable', {'channel': 'ExperimentChannel', 'experiment': '4', "location": 'pi'}))
