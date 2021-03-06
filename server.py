import socket
import threading
import time


class Server():
    ADDRESS = '127.0.0.1'
    PORT = 55555
    clients = dict()
    run = True

    def set_serv(self):
        self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serv.bind((self.ADDRESS, self.PORT))
        self.serv.listen()

    def send_to_all(self, msg):
        for client in self.clients.values():
            client.send(msg)

    def hear_and_send(self, client):
        while self.run:
            try:
                msg = client.recv(1024)
                self.send_to_all(msg)
            except Exception as e:
                if client in self.clients.values():
                    nick = self.clients.pop(client)
                    client.close()
                    self.send_to_all(
                        f'User {nick} lef the chat'.encode('utf-8'))
                    print(f'Exception while broadcasting:\n{e}')
                    break
        self.serv.close()

    def command_line(self):
        print('Use .command for action, .help for list of commands')
        while self.run:
            command = input('>>>')
            if command[0] != '.':
                print('Wrong command type use .command')
            else:
                if command == '.help':
                    print(
                        '-- .user show dictionary of users connected \n-- .kick user_name close user connection\n-- .shutdown close server \n')
                elif command == '.user':
                    for i, user in enumerate(self.clients.keys()):
                        print(f'{i + 1}: {user}')
                elif command[:5] == '.kick':
                    try:
                        nick = command.split()[1].strip()
                        client = self.clients[nick]
                        client.send(
                            'You were kicked from the server'.encode('utf-8'))
                        client.close()
                        self.clients.pop(nick)
                        self.send_to_all(
                            f'{nick} was kicked out of the server'.encode('utf-8'))
                        print(f'{nick} was kicked out of the server')
                    except IndexError:
                        print('Something was typed wrong')
                    except KeyError:
                        print('No such user exists')
                elif command == '.shutdown':
                    # send 5sec countdown till shutdown
                    for sec in range(5, 0, -1):
                        self.send_to_all(
                            f'Server shout down in {sec}s'.encode('utf-8'))
                        time.sleep(1)
                    for client in self.clients.values():
                        client.close()
                    self.run = False
                else:
                    print('No such command')

    def start_server(self):
        command_line = threading.Thread(target=self.command_line)
        command_line.start()
        print('Accepting connections')
        while self.run:
            # accept connectionas and get user login nick
            client, address = self.serv.accept()
            print(f'{str(address)} has connected')
            client.send(f'NICK'.encode('utf-8'))
            nick = client.recv(1024).decode('utf-8')
            print(f'and choosen nick: {nick}')
            # save user to client dict with nick as key
            self.clients[nick] = client
            msg = f'You have succesfully connected {nick}'
            client.send(msg.encode('utf-8'))
            greet = f'{nick} have connected'
            self.send_to_all(greet.encode('utf-8'))

            client_thread = threading.Thread(
                target=self.hear_and_send, args=(client,))
            client_thread.start()


def main():
    my_server = Server()
    my_server.set_serv()
    my_server.start_server()


if __name__ == '__main__':
    main()
