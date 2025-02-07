import json
import os
import time
from os import getcwd

import aioxmpp
from aiohttp import web
from aioxmpp import PresenceState, JID, disco

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
        favicon_path = os.path.join(getcwd(), 'static', 'SMIA_favicon.ico')
        # favicon_path = os.path.join(getcwd(), 'static', 'favicon.ico')
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
        self.myagent.aas_loaded_files = []  # se inicializa la lista
        print(request)
        reader = await request.multipart()
        # field = await reader.next()
        # assert field.name == 'file'
        #
        # filename = field.filename
        # size = 0
        upload_dir = os.path.join(getcwd(), 'aas_uploads')
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir)
        # filepath = os.path.join(upload_dir, filename)

        async for field in reader:
            if field.name == 'files':
                filename = field.filename
                size = 0
                filepath = os.path.join(upload_dir, filename)

                with open(filepath, 'wb') as f:
                    while True:
                        chunk = await field.read_chunk()  # 8192 bytes by default
                        if not chunk:
                            break
                        size += len(chunk)
                        f.write(chunk)

                if 'SMIA' in filename:
                    self.myagent.aas_loaded_files.append({'name': filename, 'size': size,
                                                          'capabilities': ['Negotiation', 'EfficientTransport'],
                                                          'assetconnections': ['InterfaceForHTTP']})
                else:
                    self.myagent.aas_loaded_files.append({'name': filename, 'size': size,
                                                          'capabilities': [], 'assetconnections': []})

        # return web.Response(text=f'File {filename} uploaded successfully, {size} bytes received.')
        self.myagent.aas_loaded = True
        return {"status": "OK"}

    async def capability_request_controller(self, request):
        try:
            data = await request.json()
            # Process the data as needed
            print("Received data:", data)

            # TODO manual test
            cap_request_data = {'capabilityName': data['name'],
                                'skillName': data['skill']['name'],
                                'skillParameterValues': {data['skill']['parameters'][0]['name']: data['skill']['parameters'][0]['value']},
                                'skillInterfaceName': data['skill']['interface']['name']}
            acl_data = {'receiver': 'gcis1',
                        'server': 'localhost',
                        'performative': 'Request',
                        'ontology': 'CapabilityRequest',
                        'thread': 'cap-request-1',
                        'messageType': 'acl',
                        'serviceID': 'capabilityRequest',
                        'serviceType': 'AssetRelatedService',
                        'serviceCategory': 'service-request',
                        'serviceParams': json.dumps(cap_request_data),
                        }

            self.myagent.cap_request_send_behav = GUIAgentBehaviours.SendBehaviour()
            self.myagent.cap_request_send_behav.msg_data = acl_data
            self.myagent.add_behaviour(self.myagent.cap_request_send_behav)
            print("Behaviour added to the agent")
            await self.myagent.cap_request_send_behav.join()
            self.myagent.acl_sent = True

            return web.json_response({"status": "success", "message": "Capability requested successfully"})
        except Exception as e:
            print("Error handling request:", e)
            return web.json_response({"status": "error", "message": "Failed to request capability"}, status=500)



    # OPERATOR METHODS
    # --------------
    async def operator_load_controller(self, request):
        print(request)

        # PRUEBA PARA DESCUBRIR AGENTES
        # Conectar al servidor XMPP
        async with self.myagent.client.connected():
            # Crear un objeto de servicio de descubrimiento
            disco_client = self.myagent.client.summon(aioxmpp.DiscoClient)

            # Obtener los elementos (agentes) registrados en el servidor
            result = await disco_client.query_items(
                JID.fromstr(self.myagent.jid.domain)  # Dominio del servidor
            )

            # Extraer los JIDs de los agentes
            agents = [str(item.jid) for item in result.items]
            print(agents)
        # --- fin de la prueba



        return {"status": "success", "reason": "success reason"}
        # return {"status": "error", "reason": "error reason"}

    async def operator_request_controller(self, request):

        data = await request.post()

        # Extract arrays for each field
        smia_id_list = data.getall('smia_id[]', [])
        asset_id_list = data.getall('asset_id[]', [])
        selected = data.getall('checkbox[]', [])
        capability = data.get('capability', None)   # Default if missing
        constraint_name = data.get('constraint_name', None)
        constraint_value = data.get('constraint_value', None)
        skill = data.get('skill', None)

        # Group data by row index
        processed_data = []
        for idx, row_id in enumerate(smia_id_list):
            if row_id in selected:
                processed_data.append({
                    "smiaID": row_id,
                    "assetID": asset_id_list[idx],
                })
        print("Requested SMIAs: {}".format(processed_data))

        if len(processed_data) > 1:
            print("There are multiple SMIAs: negotiation is required")
        else:
            print("There is only one SMIA. Requesting [{}] capability...".format(capability))

        # return web.json_response({'status': 'OK'})
        return {'status': 'OK'}