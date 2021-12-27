import pandas as pd
import numpy as np
import argparse
import glob
import os
import shutil

GAME_RESULT_COLS = ['PTS', 'REB', 'AST', 'GS40', 'OFF', 'DEF',
       'STL', 'BL', 'TOV', 'BLA', 'PF', '2P', '2P%', '3P', '3P%', 'FT', 'FT%',
       'TS%', 'P40', 'R40', 'A40', 'EF40', 'T40', 'S40', 'B40', 'FTA40']


def create_player_list(names):
    """
    Create a function to better format the list of players. The input will be a list of names with commas seperating players.
    For example: ['daniel,', 'steph', 'curry'] => ['daniel', 'steph curry']
    """
    if names is None:
        return None

    # Iterate through the list of names
    final_list = []
    cur_name = []
    for name in names:
        has_comma = ',' == name[-1]
        # Remove the comma if it's there
        cur_name.append(name.replace(',', ''))

        # If there is a comma then create the final name
        if has_comma:
            final_list.append(' '.join(cur_name))
            cur_name = []

    # Add the name that didn't have a comma
    final_list.append(' '.join(cur_name))

    return final_list

def match_player(player_names, filename):
    """
    Create a function to better match the input list of player names with a file name.
    """
    file_full_name = filename.split(' ')
    for player in player_names:
        player_full_name = player.lower().split(' ')

        file_contains = sum([file_name in player_name for file_name in file_full_name for player_name in player_full_name])
        player_contains = sum([player_name in file_name for file_name in file_full_name for player_name in player_full_name])

        if max(file_contains, player_contains) == min(len(player_full_name), len(file_full_name)):
            return True, player

    return False, None


def process_file(filename):
    """
    A function to read in a file and process split data.

    return: a dictionary of dataframes by the split type.
    """
    player_name = filename.split('/')[-1].split('.csv')[0]
    df = pd.read_csv(filename, engine='python', skiprows=2)
    indices = df[df['SPLIT'] == 'SPLIT'].index.tolist() 
    indices = [0] + indices + [len(df)]

    split_dfs = {}
    splits = ['game_result', 'time', 'opponent', 'location']

    if len(indices) - 1 != len(splits):
        print("Unexpected number of splits {}".format(len(indices) - 1))
    
    for i in range(0, len(indices) - 1):
        temp_df = df.iloc[indices[i] + 1 : indices[i + 1]]
        temp_df = temp_df.join(pd.DataFrame(np.repeat(player_name, len(temp_df)), columns=['PLAYER'], index = temp_df.index))
        split_dfs[splits[i]] = temp_df

    return (player_name, split_dfs)

def process_directory(directory, players):
    """
    A function to process all split data in a directory.

    return: a list of dictionaries with split dataframes.
    """
    all_dfs = []
    # Create the directory to search
    directory += '/' if directory[-1] != '/' else ''

    # Create the list of players to search for, we will remove them as we find them
    player_list = create_player_list(players)
    print("Looking for players {}".format(player_list))

    for file in glob.glob(directory + '*.csv'):
        if player_list is not None:
            found, player = match_player(player_list, file.split('/')[-1].split('.csv')[0])
            if found:
                all_dfs.append(process_file(file))
                player_list.remove(player)
                
        else:
            all_dfs.append(process_file(file))

    if player_list is not None and len(player_list) > 0:
        raise ValueError("Invalid player names: {}. Please remember the names of the players should  ".format(player_list) + \
         "be seperated by \",\". For more help run \"python3 process_data.py --h\"")
    
    return all_dfs

def analyze_player(player_name, split_dict, split_category, output_directory):
    all_results = []
    

    outdir = output_directory.replace('/', '')
    if len(glob.glob(outdir)) == 0:
        os.mkdir(outdir)
    else:
        if os.path.exists(outdir + '/' + player_name + '.txt'):
            os.remove(outdir + '/' + player_name + '.txt')

    if split_category == 'all':
        text_string = player_name.upper() + ' RESULTS: \n\n\n'
        for key in split_dict.keys():
            result = analyze_split(key, split_dict[key], output_directory, text_string)
            if len(result) > 0:
                all_results.append(result)

    elif split_category in split_dict.keys():
        text_string = player_name.upper() + ' RESULTS: \n\n\n'
        result = analyze_split(split_category, split_dict[split_category], output_directory, text_string)
        if len(result) > 0:
            all_results.append(result)

    else:
        raise ValueError("Invalid split category {}".format(split_category))

    return all_results

def analyze_split(split_name, split_df, outdir, text_string):
    player_name = split_df['PLAYER'].unique()[0]

    cols_of_interest = []
    for col in GAME_RESULT_COLS:
        try:
            split_df[col] = split_df[col].astype(float)
            cols_of_interest.append(col)
        except:
            continue
    
    stddevs = np.sqrt(np.var(split_df[cols_of_interest].values, axis = 0))
    means = np.mean(split_df[cols_of_interest].values, axis = 0)

    results = {}
    for index, row in split_df.iterrows():
        split = row['SPLIT']
        
        anomalies = {}
        for i in range(0, len(cols_of_interest)): 
            col = cols_of_interest[i]
            if abs(row[col] - means[i]) > 2. * stddevs[i]:
                anomalies[col] = [row[col], means[i], stddevs[i]]

        if len(anomalies) > 0:
            text_string += "{} during {} has the following anomalies...\n".format(player_name, split)
            text_string += str(pd.DataFrame(anomalies, index = ["anomaly", "avg.", "std. dev."])) + "\n"
            results[split] = anomalies

    with open('{}/{}.txt'.format(outdir, player_name), 'a') as f:
        f.write(text_string)
        f.close()

    return results
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Module to read in Basketball Reference split data. Example usage is \"python3 process_data.py Data/ --s game_result --p daniel, steph curry\"')
    parser.add_argument('directory', type=str, help='The directory of basketball data.')
    parser.add_argument('--o', dest = 'outdir', type=str, default='Results', help='The directory to store the results. Default is \"Results/\".')
    parser.add_argument('--s', dest = 'split_category', type = str, default = 'all', help = 'The category of splits to look at. Options are [\"game_result\", \"time\", \"opponent\", \"location\"] or \"all\". Default is all.')
    parser.add_argument('--p', dest = 'players', type = str, default = None, nargs = '...', help = 'NOTE: YOU MUST DO THIS OPTION LAST. The name of the players to gather splits for (seperated by \",\"). Defaults to all players in the directory.')
    args = parser.parse_args()

    basketball_dicts = process_directory(args.directory, args.players)

    for (player_name, split_dict) in basketball_dicts:
        analyze_player(player_name, split_dict, args.split_category, args.outdir)

    print("Finished analyzing! Output in {}".format(args.outdir))
