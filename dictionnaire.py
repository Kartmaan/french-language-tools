import pandas as pd 

# Création et initialisation de la dataframe
df = pd.read_csv("dico.csv")
df = df.sort_values('Mot')
df = df.reset_index(drop=True)

def definir(mot, printable=False):
    mot = mot.capitalize()

    D = df.loc[df['Mot'] == mot]['Définitions']
    D = eval(D.values[0])

    if printable:
        print("Mot : ", mot)
        for idx, definition in enumerate(D):
            print(f"{idx+1}) {definition}")
    
    else:
        return D

res = definir('manga')
print(res)