#Cubieboard Scheduler

###*Description*
>Scheduler application which controls a 4 channel relay module.

###*Features:*
- Schedule an output to switch on/off at the programmed time
- Select weekdays on which to make the schedule active and repeat
- Set the schedule for sunrise/sunset
- Manually control the relays from the dashboard

###*User interface*
- [Bootstrap](http://getbootstrap.com/)

###*Hardware*

- [Cubieboard](https://linux-sunxi.org/Cubieboard)
- 5V 4-Channel Relay Module

* [Using Python Program Control GPIOs](http://docs.cubieboard.org/tutorials/common/using_python_program_control_gpios)


###*Dependencies*

- tornado
- sqlite3
- SUNXI_GPIO
- [astral](http://pythonhosted.org/astral/)

###*Resources*

[Getting a Python script to run in the background (as a service) on boot](http://blog.scphillips.com/posts/2013/07/getting-a-python-script-to-run-in-the-background-as-a-service-on-boot/)

###*Initial instructions*

To create the database run

```sh
$ sudo python init/initdb.py
```
Start server
```sh
$ sudo python server.py
```

copy example_config.ini to main directory and rename it to config.ini or whatever you put in CONFIG_FILE_PATH

Problems:

problem:ntpd[] making interface scan socket: Permission denied
solution:usermod -G inet ntp
