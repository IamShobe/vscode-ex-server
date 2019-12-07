# vscode-ex-server

vscode-ex-server is a solution for closed business networks to work with vscode extensions offline.

The application mocks the requests and responses of vscode extension tab, which allows it to work as if vscode is online!

## How to start?
- Download `nginx`, `elran777/vscode-ex-server_server`, `elran777/vscode-ex-server_filewatcher` to your local network and add them to your repository.
- Sign a certificate of `marketplace.visualstudio.com` and add the certificate to all the clients (better way is to sign the certificate with an authority that exists in all clients).
- Create a folder at `/mnt/extensions/` - this is the location you should put all your extensions at.
- Create a folder named `certs` inside the `docker-compose.yaml` folder.
- Put there both `server.crt` file and `server.key` file.
- Use the `docker-compose.yaml` file to start the application using `docker-compose up` command.