import os
from os import getcwd

from aiohttp import web

from gui_features.behaviours import GUIAgentBehaviours


class GeneralGUIFeatures:

    def __init__(self, agent_object):
        self.myagent = agent_object

    # TODO PENSAR SI MOVERLOS A UN MODULO SOLAMENTE PARA LOS METODOS DEL GUI
    async def add_new_menu_entry(self, entry_name, entry_url, entry_icon):
        # Primero, se crea la entrada del menu con el metodo de SPADE
        self.myagent.web.add_menu_entry(entry_name, entry_url, entry_icon)

        # Despues, se añade la informacion al atributo con el diccionario en el agente, para que este accesible cuando
        self.myagent.web_menu_entries[entry_name] = {"url": entry_url, "icon": entry_icon}

    @staticmethod
    async def handle_favicon(request):
        favicon_path = os.path.join(getcwd(), 'static', 'favicon.ico')
        return web.FileResponse(favicon_path)

    @staticmethod
    async def bytes_to_string(request):
        data_bytes = b''
        async for line in request.content:
            data_bytes = data_bytes + line
        data_str = data_bytes.decode('utf-8')
        print(data_str)
        return data_str


    # CONTROLLERS
    # -----------
    @staticmethod
    async def hello_controller(request):
        print(request)
        return {"status": "OK"}

    async def acl_post_controller(self, request):

        self.myagent.acl_sent = False  # se inicializa en False
        print("HA LLEGADO AL POST DEL AGENTE: " + str(self.myagent.jid))
        print(request)
        data_str = await self.bytes_to_string(request)

        self.myagent.b = GUIAgentBehaviours.SendBehaviour()
        self.myagent.b.msg_data = data_str
        self.myagent.add_behaviour(self.myagent.b)
        print("Behaviour added to the agent")
        await self.myagent.b.join()
        self.myagent.acl_sent = True

        return {"status": "OK"}

    async def neg_post_controller(self, request):

        self.myagent.neg_sent = False  # se inicializa en False
        print("HA LLEGADO AL POST DEL AGENTE: " + str(self.myagent.jid))
        print(request)
        data_str = await self.bytes_to_string(request)

        self.myagent.b = GUIAgentBehaviours.NegBehaviour()
        self.myagent.b.msg_data = data_str
        self.myagent.add_behaviour(self.myagent.b)
        print("Behaviour added to the agent")
        await self.myagent.b.join()
        self.myagent.neg_sent = True

        return {"status": "OK"}

    async def aas_upload_controller(self, request):

        # TODO HACER AHORA: idea para mostrar como se estan cargando archivos, se podria habilitar cargar mas de uno, y
        #  mostrar una lista dentro del drag and drop los arhcivos subidos. Despues con el boton upload se
        #  subirían al servidor y se cargarían en una librería de AASs. Hay que ver como habilitar subir multiples

        self.myagent.aas_loaded = False  # se inicializa en False
        self.myagent.aas_loaded_file = False  # se inicializa en False
        print(request)
        reader = await request.multipart()
        field = await reader.next()
        assert field.name == 'file'

        filename = field.filename
        size = 0
        upload_dir = os.path.join(getcwd(), 'aas_uploads')
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)

        with open(filepath, 'wb') as f:
            while True:
                chunk = await field.read_chunk()  # 8192 bytes by default
                if not chunk:
                    break
                size += len(chunk)
                f.write(chunk)

        # return web.Response(text=f'File {filename} uploaded successfully, {size} bytes received.')
        self.myagent.aas_loaded = True
        self.myagent.aas_loaded_file = filename
        return {"status": "OK"}
