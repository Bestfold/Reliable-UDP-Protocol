# Reliable Transport Protocol
**A Reliable Transport Protocol to add reliability on top of UDP using:**
- Finite State Machine
- GBN sliding window
- 3-way handshakes
- Packet validating


## Description
This is based on a delivered exam for the Network and Cloudplatform subject at OsloMet. And the Finite State Machine is based on the one implemented in https://github.com/Bestfold/GameDevFoundations

This protocol is a network transport protocol designed to deliver datagrams between devices with retransmission. 
The protocol achieves reliability by setting up a connection between the sender and receiver
and using a sliding window for data control flow. To achieve reliability in the data transfer, the
protocol implements a Go Back N (GBN) sliding window, where packets sent must be
acknowledged by receiver before sending any more packets. These data packets and
acknowledgements are sent over the connection created, and should a packet be missing or
arrive out-of-order, the sender will be missing an acknowledgement for said packet. The
sender waits for a default time of 400ms, before assuming the packet was lost and resending
every packet in the window, because any out-of-order packet will be discarded by the
receiver.
UDP is connection-less, meaning it does not set up a connection between sender and
receiver. To allow reliable transfer of data, the protocol sets up a connection much like how TCP
does, by initiating a three-way-handshake to create, and another handshake for connection
teardown. The protocol connection differs from TCP by not having a three-way-handshake for
the teardown with FIN, FIN-ACK and last ACK, but instead using FIN and FIN-ACK.


## Finite State Machine
I chose to implement the protocol using a Finite State Machine (FSM) because it adds a
stable and easily debugged structure where what functionality should be executed at certain
moments and circumstances is easily defined. It is also how TCP is implemented, and the
naming and general function of each DRTP-state is inspired by TCP’s states (IBM, without
date)
The Finite State Machine I have implemented is an object based Mealy Machine (Wikipedia,
2023). I originally built for a personal game development project based on a creator’s guide
(The Shaggy Dev, 2023). To fit the requirements of the DRTP I have made necessary
modifications to the code and rewritten the code in Python (from Godot’s GDScript).
For the FSM to work, all the applications functionality is divided into states, like the state
LISTEN where the functionality of listening for incoming SYN-packets is written. The FSM
works by holding an instance of the current state and passing function calls down to execute
its code. The FSM changes what state the current state is when the current state returns a
reference to one of the other state-instances, meaning that the state transfers are decided by
the code written in the states, but handled by the FSM.
Overview of state flow:

<img width="646" height="521" alt="image" src="https://github.com/user-attachments/assets/2969ced1-c7a1-422e-ab73-606c539d44e3" />


Each state described:
- CLOSED: Initial state which proceeds to LISTEN if server and SYN_SENT if client. It is also the ending state which closes the connection
- LISTEN: Listens for connection requests. Proceeds to SYN_RECVD when a SYN-packet is received.
- SYN_RECVD: Sends a SYN_ACK-packet and awaits an ACK-packet before proceeding to ESTABLISHED
- SYN_SENT: Sends a SYN-packet and awaits a SYN_ACK-packet before proceeding to ESTABLISHED where the last ACK-packet is sent for the connection to be made.
- ESTABLISHED: Handles reliable data transfer. If sender, state sends ACK-packet to receiver as last part of initial handshake. Proceeds to FIN_WAIT when sender has gotten 	all data acknowledged, or LAST_ACK if receiver has received a FIN-packet.
- FIN_WAIT: Send FIN-packet to receiver. Await FIN_ACK-packet before proceeding to CLOSED.
- LAST_ACK: Send FIN_ACK-packet before proceeding to CLOSED.
For readability, the files which contain each state is named in all capital letters, which deviates from common practice.


## Reliable data transfer
To transport data reliably, my implementation uses a Go Back N (GBN) sliding window on top of the reliable connection. For the sender to be sure that the receiver has received a packet, the sender keeps note of what packets have been sent and waits for an ACK-packet containing the acknowledge number of the next packet, the sender then sends the packet which the ACK-packet “requested” through its acknowledge number. To keep more than one packet in flight, the GBN sliding window is used. The window always times the arrival of the acknowledgement for the first packet in the window. If the time exceeds the timeout period, the GBN sliding window resends all packets in the window. This is because on the receiving side, any out-of-order packet is discarded, meaning that if a packet is lost, all other packets after must be assumed discarded.
In my implementation I use a double ended queue (deque) for the sliding window. When a packet is sent, the entire packet is appended in the deque. This allows the application to easily append and pop packets and always keep the order of their appending. In addition, retransmitting all packets is as easy as looping over the deque and resending them.

The senders code where packets are sent if there is space in the window, file data is extracted and added to a packet if a valid ACK-packet (which also checks correct order) is received and is sent. And then the packet which was acknowledged is popped from the window:
<img width="945" height="436" alt="image" src="https://github.com/user-attachments/assets/7475383e-9ca4-4f14-bdea-ed9a2b63ea7e" />

The receivers code where a valid packet has its data extracted and an ACK-packet is sent in return:
<img width="945" height="446" alt="image" src="https://github.com/user-attachments/assets/1043981c-9148-46ae-a6d0-df8a14c38a39" />


## Reliable connection
To create a reliable connection the application needs to ensure that both sender and receiver are ready for data transfer before sending any data. And when data is no longer being sent, both sender and receiver knows and does not expect any data sent or received. This is implemented through handshakes.
**Initial three-way-handshake.**
To ensure that both sender and receiver are ready for data transfer, I have implemented a three-way-handshake which begins with:
The sender sends a SYN-packet. 
<img width="773" height="180" alt="image" src="https://github.com/user-attachments/assets/6635d3a3-464e-433d-b4a8-234b76a6e13b" />

The receiver receives and validates the packet.
<img width="824" height="232" alt="image" src="https://github.com/user-attachments/assets/988ecd93-b799-449e-b945-1d0ce460fed3" />
  
If packet is a valid SYN-packet, receiver returns a SYN_ACK-packet.
<img width="784" height="130" alt="image" src="https://github.com/user-attachments/assets/5b115fe9-d968-4487-8a43-6cc3646be1cb" />

Which the sender validates.
<img width="891" height="150" alt="image" src="https://github.com/user-attachments/assets/2567653f-eeb3-451f-904a-672a579f2730" />

Before returning the last ACK of the handshake to the receiver.
<img width="945" height="154" alt="image" src="https://github.com/user-attachments/assets/f1aaa3a8-bb39-4e95-aaea-238a33c44e22" />

If at any point any of these packets are delayed or lost, the application will wait for a default of 5 timeouts before proceeding to the CLOSED-state and close down the connection. The exception to this is the final ACK of the handshake, which will be resent along with the first window if sender has not received any acknowledgements for their sent packets, indicating that the last ACK was not received, and the connection is not established.

**Final two-way-handshake**
When all data has been transferred, a final two-way-handshake is initiated in order to make sure that the receiver knows that there is no more data to receive, and the sender knows the receiver got the knows. This handshake begins with:
The sender sends a FIN-packet to signal the start of the handshake.
<img width="945" height="133" alt="image" src="https://github.com/user-attachments/assets/d825a9e0-f5ef-47cb-bb0b-a6dd23870092" />

The receiver receives and validates the FIN-packet.
<img width="774" height="164" alt="image" src="https://github.com/user-attachments/assets/1be56756-f630-49c7-99f4-c17ca15b2da3" />

Before the receiver sends a FIN_ACK-packet in return and closing down.
<img width="945" height="183" alt="image" src="https://github.com/user-attachments/assets/ca39a05e-0b8d-4fbf-9977-ebe4cf111fb5" />

The sender waits for the FIN_ACK-packet before closing down.
<img width="810" height="225" alt="image" src="https://github.com/user-attachments/assets/a6fa0436-fa79-4d3f-bcec-c6bed9031d24" />





## Instructions 
Run with Python 3 from directory with the appropriate arguments.

Example:

'''
	python3 .\application.py -c -i 10.0.1.2 -p 8080 -f .dancing_baby.jpg -w 10
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

