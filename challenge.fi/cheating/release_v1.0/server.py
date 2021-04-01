import pygame
from pygame.locals import *
import os
import random
from gamelogic import objects
from gamelogic import world
from gamelogic import common
from gamelogic import achievements
import socket
from _thread import *
import json
import math
import time

# set SDL to use the dummy NULL video driver,
# so it doesn't need a windowing system on a headeless server.
os.environ["SDL_VIDEODRIVER"] = "dummy"


def threaded_socket(connection):
    client = objects.player(150, 150)
    clientid = client.id
    achievements.add_achievement(
        clientid, "Hello World!", "Successfully joined a game!"
    )
    gamestate.players.append(client)
    connection.sendall(bytes(json.dumps({"player_id": clientid}), "utf-8"))

    try:
        while True:
            data = connection.recv(1024).strip()
            try:
                common.parse_clientevents(clientid, data, gamestate)
            except Exception as e:
                print(e)
            connection.sendall(
                bytes(
                    json.dumps(
                        [
                            common.gamestate_to_dict(gamestate),
                            achievements.dicti[clientid],
                        ]
                    ),
                    "utf-8",
                )
            )
            time.sleep(0.01)  # slow things down
    except Exception as e:
        print(e)
    finally:
        for player in gamestate.players:
            if player.id == clientid:
                gamestate.players.remove(player)


if __name__ == "__main__":
    pygame.init()
    clock = pygame.time.Clock()

    gamestate = objects.gamestate()
    gamestate.bosses.append(objects.boss(world.WORLD_SIZE - 100, 100))
    HOST, PORT = "localhost", 9999
    # HOST, PORT = "0.0.0.0", 9999 # Allow connections from internet

    while True:
        try:
            ServerSocket = socket.socket()
            ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            ServerSocket.setblocking(False)
            ServerSocket.bind((HOST, PORT))
            ServerSocket.listen(5)

            while True:
                try:
                    try:  # Check for new clients
                        Client, address = ServerSocket.accept()
                        Client.settimeout(10)
                        print(
                            "{}: Server got request from {}".format(
                                common.timestamp(), address
                            )
                        )
                        start_new_thread(threaded_socket, (Client,))
                    except IOError:
                        pass  # No new client
                    except Exception as e:
                        print(e)
                    if len(gamestate.enemies) < world.TOTAL_ENEMIES:  # Spawn enemy
                        gamestate.enemies.append(
                            objects.enemy(random.randint(1000, world.WORLD_SIZE), -30)
                        )
                    if len(gamestate.bosses) == 0:
                        for player in gamestate.players:
                            achievements.add_achievement(
                                player.id,
                                "ENDGAME!",
                                "Someone killed the boss!! Was it you?",
                            )
                        time.sleep(10)
                        gamestate.players = []
                        gamestate.bosses.append(
                            objects.boss(world.WORLD_SIZE - 100, 100)
                        )
                    for enemy in gamestate.enemies:
                        if enemy.shootdelay == 0:
                            for player in gamestate.players:
                                if (
                                    player.x > enemy.x - 600
                                    and player.x < enemy.x + 600
                                ):
                                    playerdir = math.atan2(
                                        (player.x - enemy.x), (player.y - enemy.y)
                                    )
                                    if playerdir < 0:
                                        playerdir += math.pi * 2
                                    playerdir -= math.pi / 2
                                    gamestate.projectiles.append(
                                        objects.projectile(
                                            enemy.x, enemy.y, playerdir, False
                                        )
                                    )
                                    enemy.shootdelay = 100
                                    break
                    for boss in gamestate.bosses:
                        if boss.shootdelay == 0:
                            for player in gamestate.players:
                                if (
                                    player.x > boss.x - 1000
                                    and player.x < boss.x + 1000
                                ):
                                    playerdir = math.atan2(
                                        (player.x - boss.x), (player.y - boss.y)
                                    )
                                    if playerdir < 0:
                                        playerdir += math.pi * 2
                                    playerdir -= math.pi / 2
                                    gamestate.projectiles.append(
                                        objects.projectile(
                                            boss.x, boss.y, playerdir, False
                                        )
                                    )
                                    boss.shootdelay = 25
                                    break

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            run = False
                    clock.tick(world.SPEED)
                    gamestate = common.physics(gamestate)
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)
