#!/usr/bin/env python
from dota2py import api as dota_api
import os
import json
from PIL import ImageFont, ImageDraw, Image
import requests


current_dir = str(os.path.dirname(os.path.abspath(__file__)))
heroes_json = current_dir + '/' + 'heroes.json'

# Define colors

COLOR_GREEN = ((0,255,200), (0,225,200))
COLOR_RED = ((255,200,200), (255,180,180))
COLOR_GRAY = ((240,240,240), (220,220,220))

class Player:
    def __init__(self, steam_id, dota_id, name, avatar, team, level, hero_name, hero_image, kills, deaths, assists):
        self.steam_id = steam_id
        self.dota_id = dota_id
        self.name = name
        self.avatar = avatar
        self.team = team
        self.level = level
        self.hero_name = hero_name
        self.hero_image = hero_image
        self.kills = kills
        self.deaths = deaths
        self.assists = assists

class MatchImageCreator:
    def __init__(self):
        self.image = ''
        self.draw = ''
        self.heroes = ''
        self.winner = ''
        self.players = []
        self.match_id = ''

        # Configure font
        self.font_normal = ImageFont.truetype(current_dir + "/" + "Verdana.ttf", 12)
        self.font_headers = ImageFont.truetype(current_dir + "/" + "Verdana.ttf", 18)

        # Configure colors
        self.background_color = (30, 38, 47)
        self.text_color = (255, 255, 255)

        # Configure spaces
        self.widths = {'hero_picture': 44, 'player_name': 150, 'level': 50, 'kills': 30, 'deaths': 30, 'assists': 30}
        self.row_height = 25

    def drawMatchBoard(self):
        self.drawBackgroundBoard()
        self.drawHeadings(10, 50)
        self.drawWinner(self.winner)
        self.drawRows(10, 70)

        filename = 'match_' + str(self.match_id) + '.png'
        self.image.save(filename)

        return filename

    def drawHeadings(self, startX, startY):
        color = (36, 47, 57)
        width = sum(self.widths.values())
        
        x = startX
        y = startY

        self.draw.rectangle((x ,y, x+width, y+self.row_height), fill=color)

        x += self.widths['hero_picture']
        self.draw.text((x+5, y+2), "Player", font=self.font_normal, fill=self.text_color)

        x += self.widths['player_name']
        self.draw.text((x+5, y+2), "Level", font=self.font_normal, fill=self.text_color)

        x += self.widths['level']
        self.draw.text((x+5, y+2), "K", font=self.font_normal, fill=self.text_color)

        x += self.widths['kills']
        self.draw.text((x+5, y+2), "D", font=self.font_normal, fill=self.text_color)

        x += self.widths['deaths']
        self.draw.text((x+5, y+2), "A", font=self.font_normal, fill=self.text_color)

    def drawRows(self, startX, startY):
        height = self.row_height #altura padrao para todas as linhas

        colorsGray = ((240,240,240), (220,220,220))

        y_spacing = 0

        x = startX
        y = startY
        
        player_count = 0
        for player in self.players:
            odd = player_count % 2
            x = startX
            y = y + y_spacing

            #definicao das cores alternaveis por dire e radiant
            if player.team == "dire": # red
                colors = ((55,48,55), (46,47,56))
            else: # green
                colors = ((49,60,54), (43,54,56))

            #desenha foto do heroi com retangulo cinza
            width = self.widths['hero_picture']
            self.draw.rectangle((x ,y , x+width, y+height), fill=colors[odd])
            im = Image.open(player.hero_image)
            im.thumbnail((width-4,height-4))
            self.image.paste(im, (x+2, y+2))
        
            x += width

            #desenha nome do player    com o retangulo da cor do time
            width = self.widths['player_name']
            self.draw.rectangle((x ,y, x+width, y+height), fill=colors[odd])
            self.draw.text((x+5, y+2), str(player.name), font=self.font_normal, fill=self.text_color)

            x += width

            #desenha level
            width = self.widths['level']
            self.draw.rectangle((x ,y, x+width, y+height), fill=colors[odd])
            self.draw.text((x+5, y+2), str(player.level), font=self.font_normal, fill=self.text_color)

            x += width

            #desenha kills
            width = self.widths['kills']
            self.draw.rectangle((x ,y, x+width, y+height), fill=colors[odd])
            self.draw.text((x+5, y+2), str(player.kills), font=self.font_normal, fill=self.text_color)

            x += width

            #desenha deaths
            width = self.widths['deaths']
            self.draw.rectangle((x ,y, x+width, y+height), fill=colors[odd])
            self.draw.text((x+5, y+2), str(player.deaths), font=self.font_normal, fill=self.text_color)

            x += width

            #desenha assists
            width = self.widths['assists']
            self.draw.rectangle((x ,y, x+width, y+height), fill=colors[odd])
            self.draw.text((x+5, y+2), str(player.assists), font=self.font_normal, fill=self.text_color)

            player_count += 1
            # If the next player is dire, add more spacing
            if player_count != 5:
                y_spacing = 25
            else:
                y_spacing = 50

    def drawWinner(self, team):
        self.draw.text((10, 10), team + " victory", font=self.font_headers, fill=self.text_color)

    def drawBackgroundBoard(self):
        self.image = Image.new('RGB', (645, 350), self.background_color)
        self.draw = ImageDraw.Draw(self.image)

class DotaHandler:
    def __init__(self):
        token_dir = str(os.path.dirname(os.path.abspath(__file__)))
        self.steam_token_file = token_dir + '/steam_token.txt'
        self.steam_token = open(self.steam_token_file, 'r').read().strip()
        dota_api.set_api_key(self.steam_token)

        self.heroes = ''

        self.loadHeroesJson()

    def getPlayerInfo(self, steam_id):
        if int(self.steamIdToDotaId(steam_id)) == 4294967295:
            return Player(steam_id, 4294967295, "Anonymous", "", "", "", "", "", "", "", "")

        url = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=' +\
               str(self.steam_token) + '&steamids=' + str(steam_id) + '&format=json'
        r = requests.get(url)
        player_info = json.loads(r.text.replace("\n", "").replace("\t", ""))

        name = player_info["response"]["players"][0]["personaname"]
        avatar = player_info["response"]["players"][0]["avatar"]
        dota_id = self.steamIdToDotaId(steam_id)

        return Player(steam_id, dota_id, name, avatar, "", "", "", "", "", "", "")

    def loadHeroesJson(self):
        with open(heroes_json) as data_file:    
            self.heroes = json.load(data_file)["heroes"]

    def getHeroName(self, hero_id):
        for hero in self.heroes:
            if int(hero["id"]) == hero_id:
                return hero["localized_name"]

    def getHeroImage(self, hero_id):
        for hero in self.heroes:
            if int(hero["id"]) == hero_id:
                return current_dir + "/heroes/" + str(hero["name"]) + '_full.png'

    def steamIdToDotaId(self, steam_id):
        return steam_id - 76561197960265728

    def dotaIdToSteamId(self, dota_id):
        return dota_id + 76561197960265728

    def getLastMatch(self, account_id):
        # Get last match
        last_match = dota_api.get_match_history(account_id=account_id)["result"]["matches"][0]
        match_details = dota_api.get_match_details(last_match["match_id"])

        players = []

        # Create List of Players
        player_count = 0
        for player_json in match_details["result"]["players"]:
            # Create player with basic information (name, steam id, dota id, avatar)
            player = self.getPlayerInfo(self.dotaIdToSteamId(int(player_json["account_id"])))
            player.hero_name = self.getHeroName(int(player_json["hero_id"]))
            player.hero_image = self.getHeroImage(int(player_json["hero_id"]))
            player.level = player_json["level"]
            player.kills = player_json["kills"]
            player.deaths = player_json["deaths"]
            player.assists = player_json["assists"]

            if player_count < 5:
                player.team = "radiant"
            else:
                player.team = "dire"

            players.append(player)

            player_count += 1

        # Create an object of MatchImageCreator
        drawer = MatchImageCreator()
        drawer.players = players

        drawer.winner = "Radiant" if match_details["result"]["radiant_win"] == True else "Dire"

        drawer.match_id = last_match["match_id"]

        filename = drawer.drawMatchBoard()

        photo_file = open(filename, 'rb')

        os.remove(filename)

        caption = "http://www.dotabuff.com/matches/" + str(last_match["match_id"])

        return [photo_file, caption]

    def getInfoFromOldMatches(self, acc_id, n_of_matches, lastmatch):
        response_info = ''

        # Get a list of recent matches for the player
        matches = dota_api.get_match_history(account_id=acc_id)["result"]["matches"]

        if len(matches) <= 0:
            return "Failed to get matches"

        acc_id_32b = acc_id - 76561197960265728

        match_count = 0
        # Get the details for n matches match
        for match in matches:
            if match_count > n_of_matches - 1:
                break
            match_details = dota_api.get_match_details(match["match_id"])

            player_count = 0
            player_team = 'radiant'
            for player in match_details["result"]["players"]:
                if player["account_id"] == self.steamIdToDotaId(acc_id):
                    if (player_count < 5):
                        player_team = 'radiant'
                    else:
                        player_team = 'dire'
                    break
                player_count = player_count + 1

            if player_team == 'radiant' and match_details["result"]["radiant_win"] == True:
                victory = "won"
            elif player_team == 'dire' and match_details["result"]["radiant_win"] == False:
                victory  = "won"
            else:
                victory = "lost"
            response_info = response_info + "Match id: " + str(match["match_id"]) + " - " + "Player " + victory + "!\n"
            match_count = match_count + 1

        # Return the response
        return response_info

    def handleCommands(self, message):
        message = message.strip()
        args = message.split(" ")

        if len(args) != 2:
            return "Could not complete the dota command, wrong args. Usage: /dota nick number_of_matches\nor /dota lastmatch nick"

        lastmatch = False

        if message.find("lastmatch") >= 0:
            lastmatch = True
            nick = args[1]
        else:
            nick = args[0]
            n_of_matches = args[1]

        try:
            # Get player account ID
            account_id = int(dota_api.get_steam_id(nick)["response"]["steamid"])
        except:
            return "Failed to get steam id from " + nick

        if lastmatch:
            return ["photo", self.getLastMatch(account_id)]
        else:
            return ["text", self.getInfoFromOldMatches(account_id, int(n_of_matches), lastmatch)]
