#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import logging
import sys
from pathlib import Path

import pandas as pd

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-o', '--output', choices=['csv', 'excel'], default='csv')
args = arg_parser.parse_args()

input_path = Path('input')
output_path = Path('output')


def remove_list_and_dict(data):
    new_data = {}
    for key, value in data.items():
        if not type(value) is list and not type(value) is dict:
            new_data[key] = value
    return new_data


def flatten(data):
    flat_data = remove_list_and_dict(data)
    if 'playerData' in data:
        flat_data = flat_data | data['playerData']
    if 'playerStats' in data:
        flat_data = flat_data | flatten_player_stats(data['playerStats'])
    return flat_data


def flatten_player_stats(player_stats):
    flat_players_stats = remove_list_and_dict(player_stats)

    for key, value in player_stats['pokemonCaughtByType'].items():
        flat_players_stats[key.lower() + 'PokemonCaught'] = value

    master_league_stats = player_stats['battleLeagueStats']['masterLeague']
    great_league_stats = player_stats['battleLeagueStats']['greatLeague']
    ultra_league_stats = player_stats['battleLeagueStats']['ultraLeague']
    flat_players_stats['masterLeagueBattlesTotal'] = master_league_stats['battlesTotal']
    flat_players_stats['masterLeagueBattlesWon'] = master_league_stats['battlesWon']
    flat_players_stats['greatLeagueBattlesTotal'] = great_league_stats['battlesTotal']
    flat_players_stats['greatLeagueBattlesWon'] = great_league_stats['battlesWon']
    flat_players_stats['ultraLeagueBattlesTotal'] = ultra_league_stats['battlesTotal']
    flat_players_stats['ultraLeagueBattlesWon'] = ultra_league_stats['battlesWon']

    return flat_players_stats


if __name__ == "__main__":
    if not input_path.exists():
        logging.critical("No input folder found")
        sys.exit(0)

    output_path.mkdir(exist_ok=True)

    accounts = []
    for file_path in input_path.iterdir():
        if file_path.suffix != '.json':
            logging.critical(f"Unexpected file '{file_path}', only JSON files are allowed")
            sys.exit(0)
        with open(file_path, encoding='utf-8') as f:
            data = json.load(f)
            if type(data) is list:
                for account in data:
                    accounts.append(flatten(account))
            else:
                accounts.append(flatten(data))
    df = pd.DataFrame(accounts)
    if args.output == 'csv':
        df.to_csv(output_path / 'accounts.csv', encoding='utf-8', index=False)
    elif args.output == 'excel':
        df.to_excel(output_path / 'accounts.xlsx', index=False)
