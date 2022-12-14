
"""
A Workflow App using the DCR Active Repository

TODO:
    0) Fill in the template and make sure you understand how it works
    1) Make the app show only enabled-or-pending activities - and it shows an exclamation mark (!) After a pending activity
    2) When there are no more enabled-or-pending activities it deletes the simulation id.
    3) Extra: Add a button to delete the simulation in the "Instance window".

"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

import httpx
import xml.etree.ElementTree as ET


class WorkflowApp(toga.App):

    def startup(self):
        self.graph_id=1480020  # change to your own graph id
        self.simulationwindow=0

        login_box = toga.Box(style=Pack(direction=COLUMN))
        login = toga.Button(
            'Login',
            on_press=self.show_login_window,
            style=Pack(padding=5)
        )
        login_box.add(login)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = login_box
        self.main_window.show()

    def show_login_window(self, widget):
        self.second_window = toga.Window(title='Login')
        self.windows.add(self.second_window)
        login_box = toga.Box(style=Pack(direction=COLUMN))

        username_box = toga.Box(style=Pack(direction=ROW, padding=5))
        user_label = toga.Label(
            'Username: ',
            style=Pack(padding=(0, 10))
        )
        self.user_input = toga.TextInput(style=Pack(flex=1), placeholder='enter your DCR email', value='wadi.38@hotmail.com') # hint use "value = your email" to not have to retype it all the time
        username_box.add(user_label)
        username_box.add(self.user_input)

        password_box = toga.Box(style=Pack(direction=ROW, padding=5))
        passwd_label = toga.Label(
            'Password: ',
            style=Pack(padding=(0, 10))
        )
        self.password_input = toga.PasswordInput(style=Pack(flex=1))
        password_box.add(passwd_label)
        password_box.add(self.password_input)

        login_button = toga.Button(
            'Login',
            on_press=self.login,
            style=Pack(padding=5)
        )

        login_box.add(username_box)
        login_box.add(password_box)
        login_box.add(login_button)

        self.second_window.content = login_box
        self.second_window.show()

    async def login(self, widget):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}/sims",
                                        auth=(self.user_input.value, self.password_input.value))
        print(response)
        root = ET.fromstring(response.text)
        self.sims = {}
        self.username = self.user_input.value
        self.password = self.password_input.value
        for s in root.findall("trace"):
            print(f"[i] id: {s.attrib['id']}, title: {s.attrib['title']}")
            self.sims[s.attrib['id']] = "Instance:"+s.attrib['id']
        self.second_window.close()
        self.show_sim_list()

    def show_sim_list(self):
        container = toga.ScrollContainer(horizontal=False,)
        self.sims_box = toga.Box(style=Pack(direction=COLUMN))
        container.content = self.sims_box
        for id, name in self.sims.items():
            g_button = toga.Button(
                name,
                on_press=self.show_enabled_activities,
                style=Pack(padding=5),
                id = id
            )
            self.sims_box.add(g_button)
        g_button = toga.Button(
                "Create new instance",
                on_press=self.create_show_enabled_activities,
                style=Pack(padding=5)
        )
        delete_button = toga.Button(
                "Delete instance",
                on_press=self.delete_instance,
                style=Pack(padding=5)
        )
        self.sims_box.add(g_button)
        self.sims_box.add(delete_button)
        self.main_window.content = container

    async def delete_instance(self, widget):
        last_sim_id = list(self.sims.items())[-1][0]
        # Get the last simulation button. [-3] to ignore the Delete and Create instance buttons.
        last_instance_widget = self.sims_box.children[-3]
        print(last_sim_id)
        async with httpx.AsyncClient() as client:
            # Delete the instance
            response = await client.delete(f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}/sims/{last_sim_id}", 
                                           auth=(self.username, self.password))
            print("DETELE RESPONSE: ", response)
        self.main_window.info_dialog(
        "Success!",
        f"Deleted instance: {last_sim_id}")
        
        # Removes the instance button from the layout and the simulation itself from the dict. 
        self.sims.popitem()
        self.sims_box.remove(last_instance_widget) 

        
    async def show_enabled_activities(self, widget):
        self.sim_id = widget.id
        enabled_events = await self.get_enabled_events()
        print(enabled_events.json())
        root = ET.fromstring(enabled_events.json())
        events = root.findall('event')
        self.show_activities_window(events)

    async def create_show_enabled_activities(self, widget):
        async with httpx.AsyncClient() as client:
            response = await client.post(f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}/sims",
                                         auth=(self.username, self.password))
            self.sim_id = response.headers['simulationid']
            
            enabled_events = await self.get_enabled_events()
        print(enabled_events.json())
        root = ET.fromstring(enabled_events.json())
        events = root.findall('event')
        self.show_activities_window(events)

    def show_activities_window(self, events):
        if self.simulationwindow != 0:
              self.activities_window.close()
        self.activities_window = toga.Window(title=f'Simulation #{self.sim_id}')
        self.simulationwindow=1
        self.windows.add(self.activities_window)

        self.update_activities_box(events)
        self.activities_window.show()

    async def execute_activity(self, widget):
    # TODO: INSERT CODE HERE TO EXECUTE EVENT widget.id in simulation self.sim_id for graph self.graph.id
    #       RETURN result in response
        enabled_events = await self.get_enabled_events()
        print(enabled_events)
        #if len(response.text) == 0:
        #else:
        #    print(f'[!] {response.text}')
        if enabled_events:
            root = ET.fromstring(enabled_events.json())
            events = root.findall('event')
            for i in events:
                activity_id = i.attrib["id"]
            async with httpx.AsyncClient() as client:
                response = await client.post(f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}/sims/{self.sim_id}/events/{activity_id}",
                                        auth=(self.username, self.password))
            self.update_activities_box(events)
        else:
            print("[!] No enabled events!")

    async def get_enabled_events(self):
        url = f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}/sims/{self.sim_id}/events?filter=only-enabled"
        async with httpx.AsyncClient() as client:
            return await client.get(url,  auth=(self.username, self.password))

    def update_activities_box(self, events):
        activities_box = toga.Box(style=Pack(direction=COLUMN))
        if len(events) >= 1:
            for e in events:
                e_button = toga.Button(
                    text=e.attrib['label'],
                    on_press=self.execute_activity,
                    style=Pack(padding=5),
                    id=e.attrib['id'],
                )
                activities_box.add(e_button)
        else:
            print("[!] No events to execute!")

        self.activities_window.content = activities_box

def main():
    return WorkflowApp()
