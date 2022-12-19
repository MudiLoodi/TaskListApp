
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
        self.graph_id=1480020
        self.simulationwindow=0

        login_box = toga.Box(style=Pack(direction=COLUMN))
        login = toga.Button(
            'Login',
            on_press=self.show_login_window,
            style=Pack(padding=25, font_size=16, font_family="serif")
        )
        login_box.add(login)
        
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = login_box
        self.main_window.show()

    def show_login_window(self, widget):
        self.second_window = toga.Window(title='Login')
        self.windows.add(self.second_window)
        login_box = toga.Box(style=Pack(direction=COLUMN, alignment="center"))

        username_box = toga.Box(style=Pack(direction=COLUMN, padding=20))
        user_label = toga.Label(
            'Username ',
            style=Pack(width=100,padding=(0, 10),font_family="serif", font_size=16)
        )
        self.user_input = toga.TextInput(style=Pack(width=250,padding_left=10, font_family="serif", font_size=16), placeholder='Enter your DCR email')
        username_box.add(user_label)
        username_box.add(self.user_input)

        password_box = toga.Box(style=Pack(direction=COLUMN, padding=20))
        passwd_label = toga.Label(
            'Password ',
            style=Pack(width=100,padding=(0, 10),font_family="serif", font_size=16)

        )
        self.password_input = toga.PasswordInput(style=Pack(width=250,padding_left=10, font_family="serif", font_size=16))
        password_box.add(passwd_label)
        password_box.add(self.password_input)

        login_button = toga.Button(
            'Login',
            on_press=self.login,
            style=Pack(padding=5,font_size=16, font_family="serif", width=200)
        )
        
        self.info_label = toga.Label(
            "",
            style=Pack(padding=5, text_align="center", font_size=16, font_family="serif"))

        login_box.add(username_box)
        login_box.add(password_box)
        login_box.add(login_button)
        login_box.add(self.info_label)

        self.second_window.content = login_box
        self.second_window.show()
        
    async def generate_simulations(self):
        async with httpx.AsyncClient() as client:
            response = await client.post(f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}/sims",
                                        auth=(self.user_input.value, self.password_input.value))
            print(response)
    
    async def login(self, widget):
        if not self.password_input.value and not self.user_input.value:
            self.info_label.text = "Please enter your login credentials!"
            return
        elif not self.password_input.value or not self.user_input.value:
            self.info_label.text = f"Please enter {'a password!' if not self.password_input.value else 'an email!'}"
            return
        else:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}/sims",
                                        auth=(self.user_input.value, self.password_input.value))
                response.raise_for_status()                
                root = ET.fromstring(response.text)
                self.sims = {}
                self.username = self.user_input.value
                self.password = self.password_input.value
                for s in root.findall("trace"):
                    print(f"[i] id: {s.attrib['id']}, title: {s.attrib['title']}")
                    self.sims[s.attrib['id']] = "Instance:"+s.attrib['id']
                self.second_window.close()
                self.show_sim_list()
            # if credentials are wrong, catch 401 Unauthorized status
            except httpx.HTTPStatusError:    
                self.main_window.error_dialog("Login Failed", "Your email or password is incorrect.\nPlease try again.")
            # if no simulations are present, catch the error, generate sims and login
            except ET.ParseError:
                await self.generate_simulations()
                await self.login(None)
        

    def show_sim_list(self):
        container = toga.ScrollContainer(horizontal=False,)
        self.sims_box = toga.Box(style=Pack(direction=COLUMN, alignment="center"))
        self.options_box = toga.Box(style=Pack(direction=ROW))
        
        container.content = self.sims_box
        for id, name in self.sims.items():
            g_button = toga.Button(
                name,
                on_press=self.show_enabled_activities,
                style=Pack(padding=5, font_size=16, font_family="serif"),
                id = id
            )
            self.sims_box.add(g_button)
        g_button = toga.Button(
                "Create new instance",
                on_press=self.create_show_enabled_activities,
                style=Pack(padding=5,flex=1, font_size=14, font_family="serif")
        )
        delete_button = toga.Button(
                "Delete instance",
                on_press=self.delete_instance,
                style=Pack(padding=5,flex=1, font_size=14, font_family="serif")
        )
        self.options_box.add(g_button)
        self.options_box.add(delete_button)
        self.sims_box.add(self.options_box)
        self.main_window.content = container
        self.sims_box.refresh()

    def delete_instance(self, widget, sim_id=None):
        try:
            last_sim_id = list(self.sims.items())[-1][0]
            with httpx.Client() as client:
                # Delete the instance
                response = client.delete(f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}/sims/{last_sim_id if not sim_id else sim_id}", 
                                            auth=(self.username, self.password))
            # If no sim_id is passed, then remove the last simulation.
            if not sim_id:
                # Get the last simulation button.
                instance_widget = self.sims_box.children[-2]
                self.sims.popitem() # Remove the simualtion from the dict
                self.sims_box.remove(instance_widget) 
                self.main_window.info_dialog("Success!", f"Deleted simulation: #{last_sim_id}.")
            else:
                # Removes the instance from the simulations dict and call show_sim_list() to update the list. 
                self.sims.pop(sim_id)
                self.show_sim_list()
        except IndexError:
            self.main_window.error_dialog("Oh No!", "No simulations to delete!")
            self.show_sim_list()
            
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
            response = await client.get(f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}/sims",
                                         auth=(self.username, self.password))
            enabled_events = await self.get_enabled_events()
        print(enabled_events.json())
        root = ET.fromstring(enabled_events.json())
        events = root.findall('event')
        
        root = ET.fromstring(response.text)
        # Add the new instance to the dict
        for sub_elem in root.findall("trace"):
            self.sims[sub_elem.attrib['id']] = "Instance:"+sub_elem.attrib['id']
        # call show_sim_list() to update the instance list to show the newly added instance
        self.show_sim_list()
        self.show_activities_window(events)
        

    def show_activities_window(self, events):
        """Shows the window that contains the activites for a given simulation."""
        if self.simulationwindow != 0:
              self.activities_window.close()
        self.activities_window = toga.Window(title=f'Simulation #{self.sim_id}')
        self.simulationwindow=1
        self.windows.add(self.activities_window)

        self.update_activities_box(events)
        self.activities_window.show()

    async def execute_activity(self, widget):
        event_id = widget.id
        async with httpx.AsyncClient() as client:
            response = await client.post(f"https://repository.dcrgraphs.net/api/graphs/{self.graph_id}/sims/{self.sim_id}/events/{event_id}",
                                    auth=(self.username, self.password))
        if len(response.text) == 0:
            enabled_events = await self.get_enabled_events()
        else:
            print(f'[!] {response.text}')
        if enabled_events:
            root = ET.fromstring(enabled_events.json())
            events = root.findall('event')
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
                    style=Pack(padding=5, font_size=14, font_family="serif"),
                    id=e.attrib['id'],
                )
                activities_box.add(e_button)
        else:
            self.main_window.info_dialog(
            "Success!",
            f"Simulation complete.\nSimulation #{self.sim_id} will now be deleted.")
            self.delete_instance(None, self.sim_id)
            self.activities_window.hide()
        self.activities_window.content = activities_box

def main():
    return WorkflowApp()
