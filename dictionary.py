import ast
from typing import Optional

import pandas as pd

# ===================================================================
#                         DATAFRAME CREATION
# ===================================================================
print("Main dataframe creation...")
df = pd.read_csv("files/dico.csv") # Dataframe creation
df = df.sort_values('Mot') # Alphabetic order
df = df.dropna() # Remove missing data
df = df.reset_index()

# ===================================================================
#                             FUNCTION
# ===================================================================
def define(dataframe: pd.DataFrame, word_column_name: str, definition_column_name: str, word: str) -> Optional[list]:
    """
    Displays the definition of a word in the word dictionary.

    Args:
        dataframe (pandas.DataFrame): Pandas dataframe with a word column and a definition column.
        word_column_name (str): Name of the column containing the words.
        definition_column_name (str): Name of column containing definitions.
        word (str): Word to search.

    Returns:
        (list): List containing the definition(s) of the word searched for.
        (None): If the word is not in the dictionary.
    """
    print("Searching...")

    word = word.capitalize()

    definition = dataframe.loc[df[word_column_name] == word][definition_column_name]

    # WORD NOT FOUND
    if len(definition) == 0:
        print(f"'{word}' not in dictionary")
        return None

    # WORD FOUND
    # Definitions in the dataframe are stored as strings representing lists. To convert these strings into usable
    # `list` objects, we use `ast.literal_eval`, a more secure method than `eval` as it only evaluates Python literals
    # (lists, dictionaries, etc.), without executing arbitrary code.
    else:
        definition = ast.literal_eval(definition.values[0])

    return definition

# ===================================================================
#                              MAIN
# ===================================================================
if __name__ == "__main__":
    word_to_define = "hallali"
    word_definition = define(df, "Mot", "Définitions", word_to_define)
    print(f"{word_to_define}:")
    print(word_definition)