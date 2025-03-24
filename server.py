from aiohttp import web, WSMsgType
import aiosqlite
import asyncio
import re
import os
import json
from pathlib import Path
from datetime import datetime
from asyncio import Lock, Semaphore

DB_NAME = 'calculator.db'
HISTORY_LIMIT = 1000
MAX_WORKERS = 10
REQUEST_TIMEOUT = 30

class WebSocketManager:
    def __init__(self):
        self.active_connections = set()
        self.history = []
        self.lock = Lock()
        self.queue = asyncio.Queue(maxsize=1000)
        self.semaphore = Semaphore(MAX_WORKERS)
        self.is_running = True

    async def process_queue(self):
        while self.is_running:
            async with self.semaphore:
                try:
                    client_ip, expression, mode = await self.queue.get()
                    await self.process_task(client_ip, expression, mode)
                except Exception as e:
                    print(f"Queue processing error: {e}")
                finally:
                    self.queue.task_done()

    async def process_task(self, client_ip, expression, mode):
        try:
            result, error = await self.calculate(expression, mode)
            async with self.lock:
                await self.save_to_db(
                    expression=expression,
                    mode=mode,
                    result=result,
                    error=error,
                    client_ip=client_ip
                )
                
                self.history.append({
                    'id': len(self.history) + 1,
                    'timestamp': datetime.now().isoformat(),
                    'expression': expression,
                    'mode': mode,
                    'result': result,
                    'error': error,
                    'client_ip': client_ip
                })
                
                await self.broadcast_history()
                
        except Exception as e:
            print(f"Task processing failed: {e}")

    async def calculate(self, expression, mode):
        proc = await asyncio.create_subprocess_exec(
            'build/app.exe',
            mode,
            expression,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10)
            return stdout.decode().strip(), stderr.decode().strip()
        except asyncio.TimeoutError:
            return None, "Calculation timeout"

    async def save_to_db(self, **data):
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute('''
                INSERT INTO history 
                (expression, mode, result, error, client_ip, timestamp)
                VALUES (?,?,?,?,?,?)
            ''', (
                data['expression'],
                data['mode'],
                data['result'],
                data['error'],
                data['client_ip'],
                datetime.now().isoformat()
            ))
            await db.commit()

    async def broadcast_history(self):
        try:
            message = json.dumps({
                'type': 'history_update',
                'data': self.history[-100:]  # Отправляем последние 100 записей
            })
            
            dead_connections = []
            for ws in self.active_connections.copy():
                try:
                    await ws.send_str(message)
                except ConnectionResetError:
                    dead_connections.append(ws)
            
            for ws in dead_connections:
                self.active_connections.remove(ws)
                
        except Exception as e:
            print(f"Broadcast failed: {e}")

    async def shutdown(self):
        self.is_running = False
        await self.queue.join()
        for ws in self.active_connections:
            await ws.close()

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,timestamp DATETIME NOT NULL,
                expression TEXT NOT NULL,
                mode TEXT NOT NULL,
                result TEXT,
                error TEXT,
                client_ip TEXT NOT NULL
            )
        ''')
        await db.commit()

async def websocket_handler(request):
    ws = web.WebSocketResponse(timeout=REQUEST_TIMEOUT)
    await ws.prepare(request)
    
    manager = request.app['ws_manager']
    client_ip = request.transport.get_extra_info('peername')[0]
    
    async with manager.lock:
        manager.active_connections.add(ws)
        try:
            await ws.send_json({
                'type': 'full_history',
                'data': manager.history[-100:]
            })
        except ConnectionResetError:
            manager.active_connections.remove(ws)
            return ws

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                data = json.loads(msg.data)
                if data['type'] == 'new_expression':
                    await manager.queue.put((
                        client_ip,
                        data['expression'],
                        data.get('mode', 'int')
                    ))
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        async with manager.lock:
            manager.active_connections.discard(ws)
            
    return ws

async def start_background_tasks(app):
    await init_db()
    asyncio.create_task(app['ws_manager'].process_queue())

async def on_shutdown(app):
    await app['ws_manager'].shutdown()

def main():
    app = web.Application()
    app['ws_manager'] = WebSocketManager()
    
    app.on_startup.append(start_background_tasks)
    app.on_shutdown.append(on_shutdown)
    
    app.router.add_get('/ws', websocket_handler)
    
    web.run_app(
        app,
        port=8000,
        handle_signals=True,
        reuse_port=True
    )

if __name__ == '__main__':
    main()
