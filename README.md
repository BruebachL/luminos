![Luminos](https://raw.githubusercontent.com/BruebachL/luminos/master/resources/splash_screen.png)
===========
# Installation

## Windows

1. Download Python 3.10 installer (https://www.python.org/downloads/release/python-3108/) [Windows installer at the bottom]
2. Run the setup (Ensure you've checked 'Add Python to PATH')
3. Open File Explorer and navigate to the luminos folder.
4. Install Luminos by clicking on install.bat
5. Adjust the IP Address in config.cfg located in <luminos_main_folder>/config.cfg
6. Launch the client by clicking on launch.bat

# How does it work/Under the hood

## File Management

Internally, every client possesses a manager for certain file types (AudioManager, ClueManager, MapManager, VideoManager, etc.).

These managers are responsible for indexing their correct resource folder (e.g. luminos/resources/audio). They do this by reading in their existing index file (audio.json), hashing every file found in their resource folder and then comparing these file hashes to the entries in their index file. If a file hash without a valid entry in the index file is found, it is created. If an index entry without an existing file hash is found, it is deleted.

Index entries also hold unique information defined by the manager (e.g. duration for audio clips, display name for image files).

This allows the client and the server to request files from each other by first specifying the file type (e.g. "image:map") which lets the other side know which manager to use to access this file and then specifying a file hash, which lets the manager know which file to load.

This also allows the user to include a file in their campaign by simply pasting it into the correct resource folder. It will then be available on the next launch of the client.

## Client/Server Communication

Client and Server communicate over a TCP connection on port 1337 using serialized JSON objects. Both Client and Server expect each other to first announce the payload length (packed into 12 bytes) and then send the actual payload. This is done to avoid passing a partial transmission to the JSON deserializer. Payloads are only processed once they have been received in full.

Client and Server both import from the same commands file, which means technically, they should always be able to understand each other's commands.

Available commands are:
1. CommandUpdateClient
2. CommandUpdateClientInfo
3. CommandQueryConnectedClient
4. CommandFileRequest
5. CommandListenUp
6. CommandRollDice
7. InfoRollDice
8. InfoDiceRequestDecline
9. InfoFileRequest
10. InfoUpdateFile
11. InfoAudioFile
12. InfoVideoFile
13. InfoDiceFile
14. InfoClueFile
15. InfoMapFile
16. CommandRevealClue
17. CommandRevealMapOverlay
18. CommandPlayAudio
19. CommandPlayVideo
20. CommandPlayStinger

On connection, the client sends a ClientInfo object to the server containing information about the client, like its ID and its version numbers.

If the Server detects that the client version is lower than the server version, it will initiate an update. To do this, it engages its UpdateManager which rebuilds its index before sending it to the client. The client similarly engages its UpdateManager to hash all files, compares them against the server's files, determines which ones it is missing and then initiates a file request for each missing file. Since this is done by file hash and not file name, this detects if a file was modified.

Files which should be IGNORED during updates may be configured by including them in update.cfg