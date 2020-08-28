import pandas as pd
import xml.etree.ElementTree as ET
import sys


def merge(path):
    types = ["hospitals","houses","offices","parks","schools","supermarkets","place_of_worship"]
    frames = []
    for type in types:
        file = path+"/"+type+".csv"
        try:
            dataframe = pd.read_csv(file,names=["type","x","y","area"])
            frames.append(dataframe)
        except:
            print("file empty "+ file)
        # if dataframe.empty == True:
        #     print("file empty "+ file)
        # else:
        #     frames.append(dataframe)
    df = pd.concat(frames,ignore_index=True)
    df.to_csv(path+"/buildings.csv", index=False,header=None)

if __name__ == "__main__":
    path = sys.argv[1]
    merge(path)