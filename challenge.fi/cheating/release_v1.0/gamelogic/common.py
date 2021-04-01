from gamelogic import world
from gamelogic import objects
from gamelogic import achievements
import math
import json
import time, datetime


def gamestate_to_dict(gamestate):
    data = {}
    data["players"] = []
    data["enemies"] = []
    data["projectiles"] = []
    data["bosses"] = []
    for player in gamestate.players:
        data["players"].append(
            [
                player.id,
                player.x,
                player.y,
                player.state,
                player.dir,
                player.x_vel,
                player.y_vel,
                player.ammo,
                player.reloadleft,
                player.shoottimer,
                player.hp,
            ]
        )
    for enemy in gamestate.enemies:
        data["enemies"].append(
            [
                enemy.id,
                enemy.x,
                enemy.y,
                enemy.dir,
                enemy.x_vel,
                enemy.y_vel,
                enemy.hp,
                enemy.shootdelay,
                enemy.y_pos,
            ]
        )
    for projectile in gamestate.projectiles:
        data["projectiles"].append(
            [
                projectile.id,
                projectile.playerid,
                projectile.x,
                projectile.y,
                projectile.dir,
                projectile.friendly,
                projectile.moveremaining,
            ]
        )
    for boss in gamestate.bosses:
        data["bosses"].append([boss.id, boss.x, boss.y, boss.hp, boss.shootdelay])
    return data


def timestamp():
    return datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")


class newEvent:
    pass


def parse_clientevents(clientid, json_data, gamestate):
    clientevents = json.loads(json_data)
    for player in gamestate.players:
        if player.id == clientid:
            for clientevent in clientevents:
                event = newEvent()
                event.name = clientevent[0]
                if event.name == "jump":
                    if player.state != "jumping":
                        player.state = "jumping"
                        player.y_vel += 4
                elif event.name == "shoot":
                    if player.shoottimer == 0:
                        player.shoottimer = 15
                        event.x = clientevent[1]
                        event.y = clientevent[2]
                        event.d = clientevent[3]
                        newprojectile = objects.projectile(
                            event.x, event.y, event.d, True, playerid=clientid
                        )
                        gamestate.projectiles.append(newprojectile)
                        player.ammo -= 1
                        if distance(player, event) > 65:
                            gamestate.projectiles.remove(newprojectile)
                elif event.name == "left":
                    player.dir = -1
                elif event.name == "right":
                    player.dir = 1
                elif event.name == "stop":
                    player.dir = 0
                elif event.name == "reload":
                    player.state = "reloading"
                    player.reloadleft = 150


def update_gamestate_from_dict(old_gamestate, data):
    gamestate = objects.gamestate()
    for player in data["players"]:
        for local_player in old_gamestate.players:
            if local_player.id == player[0]:
                break
        else:
            local_player = objects.player(player[1], player[2])
        local_player.id = player[0]
        local_player.x = player[1]
        local_player.y = player[2]
        local_player.state = player[3]
        local_player.dir = player[4]
        local_player.x_vel = player[5]
        local_player.y_vel = player[6]
        local_player.ammo = player[7]
        local_player.reloadleft = player[8]
        local_player.shoottimer = player[9]
        local_player.hp = player[10]
        gamestate.players.append(local_player)
    for enemy in data["enemies"]:
        for local_enemy in old_gamestate.enemies:
            if local_enemy.id == enemy[0]:
                break
        else:
            local_enemy = objects.enemy(enemy[1], enemy[2])
        local_enemy.id = enemy[0]
        local_enemy.x = enemy[1]
        local_enemy.y = enemy[2]
        local_enemy.dir = enemy[3]
        local_enemy.x_vel = enemy[4]
        local_enemy.y_vel = enemy[5]
        local_enemy.hp = enemy[6]
        local_enemy.shootdelay = enemy[7]
        local_enemy.y_pos = enemy[8]
        gamestate.enemies.append(local_enemy)
    for projectile in data["projectiles"]:
        for local_projectile in old_gamestate.projectiles:
            if local_projectile.id == projectile[0]:
                break
        else:
            local_projectile = objects.projectile(
                projectile[2],
                projectile[3],
                projectile[4],
                projectile[5],
                playerid=projectile[6],
            )
        local_projectile.id = projectile[0]
        local_projectile.playerid = projectile[1]
        local_projectile.x = projectile[2]
        local_projectile.y = projectile[3]
        local_projectile.dir = projectile[4]
        local_projectile.friendly = projectile[5]
        local_projectile.moveremaining = projectile[6]
        gamestate.projectiles.append(local_projectile)
    for boss in data["bosses"]:
        for local_boss in old_gamestate.bosses:
            if local_boss.id == boss[0]:
                break
        else:
            local_boss = objects.boss(boss[1], boss[2])
        local_boss.id = boss[0]
        local_boss.x = boss[1]
        local_boss.y = boss[2]
        local_boss.hp = boss[3]
        local_boss.shootdelay = boss[4]
        gamestate.bosses.append(local_boss)
    return gamestate


def distance(a, b):
    return math.sqrt(pow(a.x - b.x, 2) + pow(a.y - b.y, 2))


def physics(gamestate):
    for projectile in gamestate.projectiles:
        if (
            projectile in gamestate.projectiles
        ):  # If projectile is not already destroyed
            projectile.move()
            if (
                (projectile.x < 0 or projectile.x > world.WORLD_SIZE)
                or (projectile.y < 0 or projectile.y > world.WORLD_HEIGHT)
                or projectile.moveremaining <= 0
            ):
                gamestate.projectiles.remove(projectile)
                continue
            if projectile.friendly:
                for other_projectile in gamestate.projectiles:
                    if not other_projectile.friendly:
                        if distance(projectile, other_projectile) < projectile.hitbox:
                            gamestate.projectiles.remove(projectile)
                            gamestate.projectiles.remove(other_projectile)
                            break
                else:
                    for enemy in gamestate.enemies:
                        if (
                            distance(projectile, enemy)
                            < enemy.hitbox / 2 + projectile.hitbox / 2
                        ):
                            enemy.hp -= 1
                            if enemy.hp == 0:
                                achievements.add_achievement(
                                    projectile.playerid,
                                    "First blood!",
                                    "You destroyed an enemy!",
                                )
                            gamestate.projectiles.remove(projectile)
                            break
                    else:
                        for boss in gamestate.bosses:
                            if distance(projectile, boss) < 10:
                                boss.hp -= 1
                                gamestate.projectiles.remove(projectile)
                                break
                            # Forcefield
                            if (
                                distance(projectile, boss)
                                < boss.hitbox / 2 + projectile.hitbox / 2
                            ):
                                gamestate.projectiles.remove(projectile)
                                break
            else:
                for player in gamestate.players:
                    if (
                        distance(projectile, player)
                        < player.hitbox / 2 + projectile.hitbox / 2
                    ):
                        player.hp -= 1
                        gamestate.projectiles.remove(projectile)
                        break
    for player in gamestate.players:
        for enemy in gamestate.enemies:
            if distance(enemy, player) < player.hitbox / 2 + enemy.hitbox / 2:
                player.hp -= 1
        for boss in gamestate.bosses:
            if distance(boss, player) < player.hitbox / 2 + boss.hitbox / 2:
                player.hp -= 0
        if player.hp <= 0:
            gamestate.players.remove(player)
            break
        player.move()
    for enemy in gamestate.enemies:
        if enemy.hp <= 0:
            gamestate.enemies.remove(enemy)
        enemy.move()
    for boss in gamestate.bosses:
        if boss.hp <= 0:
            gamestate.bosses.remove(boss)
        boss.move()
    return gamestate
