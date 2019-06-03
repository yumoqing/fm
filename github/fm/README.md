# fm is a file synchronous tools between difference host
## dependented packages
appPublic provide some bases functions for fm,
[watchdog](https://pypi.org/project/watchdog/) is a files or folders changes monitor engine,
[hachiko](https://github.com/biesnecker/hachiko) is the asynchronous API for watchdog
[paramiko](https://github.com/paramiko/paramiko) is a python ssh2 api

## function
fm monitors one or more local folders, and sysnchronizes the changes to the defined peer(s)

## configuratin
the configure file is located at conf folder inside the fm containers folder

the configure file named by 'config.json', it contains follows:
```
{
	"peers":{
			"peer1": {
				"host":"www.peer1.com",
				"user":"somone"
			},
			"peer2": {
				"host":"www.peer1.com",
				"port":40022,
				"user":"somone"
			}
	},
	"monitors":[
		{
			"path":"/home/someone/tmp",
			"identify_by_ok":true,
			"modified_delay":2,
			"peers":{
					"peer1": {
						"path":"/home/someone/tst"
					}
			}
		},
		{
			"path":"/home/someone/here",
			"peers":{
					"peer1": {
						"path":"/home/someone/there"
					},
					"peer2": {
						"path":"/home/someone/there"
					}
			}
		}
	]
}
```

peers:defines all peers who will synchronize the change below the local monitored folder 
each peer identifies by its name, and must have "host" and "user" attributes in peer definition, "port" will be add if that peer sshd using a user defined port

likes :
```
"peer2":{
	"host":"11.11.11.22",
	"user":"dummy",
	"port":40022
}
```

"peers" can defines as many peers as you need


"monitors" is a array contains one or more local folders will be monitored.
each items in "monitors" should have "path" and "peers",if the file synchronize dependent by its '.ok' file, a "identified_by_ok" must set to true 

"path" is a string to a local folder

"peers" indicates which peer name in the root "peers" will followed the change
