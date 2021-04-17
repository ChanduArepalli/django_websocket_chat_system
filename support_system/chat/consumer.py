import asyncio
import json
from django.contrib.auth import get_user_model as User
from channels.consumer import AsyncConsumer, SyncConsumer
from channels.db import database_sync_to_async

from .models import Thread, ChatMessage


class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print(f"connected - ", event)

        # await asyncio.sleep(10)
        other_users = self.scope['url_route']['kwargs']['username']
        print(self.scope)
        me = self.scope['user']
        print(f"Others --> {other_users}")
        print(f"me --> {me}")
        thread_obj = await self.get_thread(me, other_users)
        # print(thread_obj)
        # await self.send({
        #     'type': 'websocket.send',
        #     "text": 'new message'
        # })
        if thread_obj:
            chat_room = f"chat_room_{thread_obj.id}"
        else:
            chat_room = f"chat_room_None"
        self.chat_room = chat_room
        await self.channel_layer.group_add(
            chat_room,
            self.channel_name
        )

        await self.send({
            'type': 'websocket.accept'
        })

    async def websocket_receive(self, event):
        print(f"received - ", event)

        front_end_data = event.get('text', None)
        print("front_end_data ", front_end_data)
        try:
            msg = json.loads(event.get('text', None))['message']
            print("Client Msg --> ", msg)
            final_data = msg + ' - ' + (self.scope['user'].username if self.scope['user'] else None)
            # await self.send({
            #     'type': 'websocket.send',
            #     'text': final_data
            #     })
            await self.channel_layer.group_send(
                self.chat_room,
                {
                    "type": "chat_message",
                    "text": final_data
                }
            )
        except Exception as e:
            print("exception --> ", e)

    async def chat_message(self, event):
        print("message ", event)
        await self.send({
            "type": "websocket.send",
            "text": event['text']
        })
    async def websocket_disconnect(self, event):
        print(f"disconnected - ", event)
    
    @database_sync_to_async
    def get_thread(self, user, other_username):
        print(f'other_username --> {other_username}')
        if Thread.objects.get_or_new(user, other_username):
            return Thread.objects.get_or_new(user, other_username)[0]
        else:
            return None
