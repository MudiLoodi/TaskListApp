# TaskListApp
Task List App for the Development of Cloud-Based Health Apps course at DIKU.

TO USE IN WINDOWS
1. Clone TaskListApp, e.g. as a folder in Documents
2. In the terminal, go into the local folder "TaskListApp": 
> cd Documents\TaskListApp
3. Make a virtual environment:
> py -m venv beeware-venv

> beeware-venv\Scripts\activate.bat
4. Go into the folder "tasklistapp": 
> cd tasklistapp
5. If you want to run the app, you can do:
> briefcase dev
6. To make a product that can ship, do:
>briefcase create

>briefcase build

>briefcase package

This makes an .msi file inside the windows folder that can be double-clicked to install the app on Windows.

7. To make an android simulation of the app, do:
>briefcase create android

>briefcase build android

>briefcase run android (here I called the emulator: sundPhone)

Note that you may have to stop/remove any other android simulations for this to complete successfully.

8. Next time, you can start the android simulation with
>briefcase run android -d @sundPhone
