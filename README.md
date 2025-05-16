# Reliable Transport Protocol
**A Reliable Transport Protocol to add reliability on top of UDP**

## Instructions 
Run with Python 3 from directory with the appropriate arguments.

Example:
'''python
	python3 application.py -c -i 10.0.1.2 -p 8080 -f dancing_baby.jpg -w 10
'''

## Arguments

| Flag  | Long flag | Input | Default | Type | Description|
| :-: |:-:| - | :-: | - | - |
| -s | --server | None | None | Boolean | Enable server mode (receiver) |
| -c | --client | None | None | Boolean | Enable client mode (sender) |
| -i | --ip | Ip address | 127.0.0.1 | String | Choose the ip address for receiver to listen on, or the ip address for the sender to send to |
| -p | --port | Port number | 8080 | Boolean | Choose the port for receiver to listen on, or the port for the sender to send to. |
| -f | --file | File path | None | String | Write the name of the file to send (ignored by server) |
| -w | --window | Size | 3 | Integer | Window size for senders sliding window. (Server is hardcoded to tell the client that max is 15) |
| -d | --discard | Packet number | 1000000 | Integer | Discard the packet with sequence number equal to the provided integer. (ignored by client) |
