import pandas as pd
import numpy as np
import argparse
import glob

GAME_RESULT_COLS = ['PTS', 'REB', 'AST', 'GS40', 'OFF', 'DEF',
       'STL', 'BL', 'TOV', 'BLA', 'PF', '2P', '2P%', '3P', '3P%', 'FT', 'FT%',
       'TS%', 'P40', 'R40', 'A40', 'EF40', 'T40', 'S40', 'B40', 'FTA40']

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
        temp_df['PLAYER'] = player_name
        split_dfs[splits[i]] = temp_df

    return split_dfs

def process_directory(directory, player_name):
    """
    A function to process all split data in a directory.

    return: a list of dictionaries with split dataframes.
    """
    all_dfs = []
    directory += '/' if directory[-1] != '/' else ''
    for file in glob.glob(directory + '*.csv'):
        if player_name is not None:
            if player_name.lower() in file.split('/')[-1].split('.csv')[0].lower():
                all_dfs.append(process_file(file))
        else:
            all_dfs.append(process_file(file))
    
    return all_dfs

def analyze_player(split_dict, split_category):
    all_results = []
    if split_category == 'all':
        for key in split_dict.keys():
            result = analyze_split(key, split_dict[key])
            if len(result) > 0:
                all_results.append(result)

    elif split_category in split_dict.keys():
        result = analyze_split(split_category, split_dict[split_category])
        if len(result) > 0:
            all_results.append(result)

    else:
        print("Invalid split category {}".format(split_category))

    return all_results

def analyze_split(split_name, split_df):
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
            print("{} during {} has the following anomalies...".format(player_name, split))
            print(pd.DataFrame(anomalies, index = ["anomaly", "avg.", "std. dev."]))
            results[split] = anomalies

    return results
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Module to read in Basketball Reference split data.')
    parser.add_argument('directory', type=str, help='The directory of basketball data.')
    parser.add_argument('--p', dest = 'player_name', type = str, default = None, help = 'The name of the player to gather splits. Defaults to all players in the directory.')
    parser.add_argument('--s', dest = 'split_category', type = str, default = 'all', help = 'The category of splits to look at. Options are [\"game_result\", \"time\", \"opponent\", \"location\"] or \"all\". Default is all.')
    args = parser.parse_args()

    print(args.directory, args.player_name)
    basketball_dicts = process_directory(args.directory, args.player_name)

    for split_dict in basketball_dicts:
        analyze_player(split_dict, args.split_category)
