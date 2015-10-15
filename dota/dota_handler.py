#!/usr/bin/env python
from dota2py import api as dota_api
import os

class DotaHandler:
    def __init__(self):
        token_dir = str(os.path.dirname(os.path.abspath(__file__)))
        dota_api.set_api_key(open(token_dir + '/steam_token.txt', 'r').read().strip())

    def getInfoFromOldMatches(self, acc_id, n_of_matches):
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
                if player["account_id"] == acc_id_32b:
                    if (player_count < 5):
                        player_team = 'radiant'
                    else:
                        player_team = 'dire'
                    break
                player_count = player_count + 1

            if player_team == 'radiant' and match_details["result"]["radiant_win"] == True:
                victory = "win"
            elif player_team == 'dire' and match_details["result"]["radiant_win"] == False:
                victory  = "win"
            else:
                victory = "loose"
            response_info = response_info + "Match id: " + str(match["match_id"]) + " - " + "Player " + victory + "!\n"
            match_count = match_count + 1

        # Return the response
        return response_info

    def handleCommands(self, message):
        message = message.strip()
        args = message.split(" ")

        if len(args) != 2:
            return "Could not complete the dota command, wrong args. Usage: /dota nick number_of_matches"

        nick = args[0]
        n_of_matches = args[1]

        try:
            # Get player account ID
            account_id = int(dota_api.get_steam_id(nick)["response"]["steamid"])
        except:
            return "Failed to get steam id from " + nick

        return self.getInfoFromOldMatches(account_id, int(n_of_matches))
