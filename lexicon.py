import time
import logging
import ast
from typing import Optional, Union

import pandas as pd
from openpyxl import load_workbook, Workbook

logger = logging.getLogger()
logger.setLevel(logging.WARNING)

# ===================================================================
#                         DATAFRAME CREATION
# ===================================================================
print("Main dataframe creation...")
dict_df = pd.read_csv("dico.csv")
dict_df = dict_df.sort_values("Mot")
dict_df = dict_df.dropna()
dict_df = dict_df.reset_index(drop=True)

# ===================================================================
#                         EXCEL FILE INIT
# ===================================================================
# Opening the Excel file
excel_file = load_workbook("lexi.xlsx")
sheet = excel_file.active

# Writing of the first line: column names
sheet["A1"] = "Mot"
sheet["B1"] = "Definitions"
sheet["C1"] = "Timestamp"

# ===================================================================
#                            FUNCTIONS
# ===================================================================
# In order to reduce the risks associated with too long or potentially
# infinite iterations of the lexicon
LIMIT_ITER = 10000

def first_empty(workbook: Workbook, column: str = 'A'):
    """ Returns the index of the first empty cell in a column.

    Args:
        workbook (Workbook): Workbook object (openpyxl) referring to the spreadsheet.
        column (str): Letter of the column to be analyzed to locate the first empty cell.
    """

    idx = 2
    while True:
        # Cell is empty
        if not isinstance(workbook[f'{column}{idx}'].value, str):
            return idx

        # Cell is full
        else:
            idx += 1
            if idx == LIMIT_ITER:
                logging.critical("Too many iterations")
                break
            else:
                continue

def add_word(dataframe: pd.DataFrame, workbook: Workbook, word: str) -> Optional[None]:
    """ Addition of a word in the lexicon which is present in the dictionary.

    Args:
        dataframe (pandas.Dataframe): Dictionary dataframe.
        workbook (Workbook): Workbook object (openpyxl) referring to the spreadsheet.
        word (str): Word present in the dictionary to add in the lexicon.

    Returns:
        None: Not in dictionary or already in lexicon.
    """

    word = word.capitalize()

    definition = dataframe.loc[dataframe['Mot'] == word]['Définitions']

    # Word not found
    if len(definition) == 0:
        logging.warning(f"'{word}' not in dictionary")
        return None

    # Word found
    else:
        logging.info(f"'{word}' found in dictionary at idx {dataframe.loc[dataframe['Mot'] == word].index[0]}")
        definition = ast.literal_eval(definition.values[0])  # -> <list>

        idx = 2  # Index vertical de la colonne

        # Loop to first empty cell in lexicon
        while idx <= first_empty(workbook):

            # Word already present in the lexicon
            if workbook[f"A{idx}"].value == word:
                logging.warning(f"'{word}' not added : already in lexicon at cell A{idx}")
                return None

            # Cell is empty
            if not isinstance(workbook[f"A{idx}"].value, (str, int, float)):

                # All the definitions of the word contained in the list (D) are merged
                # into a single string in order to be inserted into the sheet cell
                definition_list = []
                for idx_def, definition in enumerate(definition):
                    definition_list.append(f"{idx_def + 1}) {definition}")

                workbook[f"A{str(idx)}"] = word  # Add word

                workbook[f"B{str(idx)}"] = "".join(definition_list)  # Add definitions

                workbook[f"C{str(idx)}"] = str(int(time.time()))  # Add timestamp

                logging.info(f"'{word}' added in lexicon at idx A{idx}")
                break

            else:
                idx += 1
                if idx == LIMIT_ITER:  # watchdog
                    logging.critical("Watchdog : too many iterations")
                    break

    excel_file.save("lexi.xlsx")  # Save file after modification
    logging.debug("xlsx file saved after adding a word")
    print(f"The word '{word}' has been added to the lexicon.")

def search(workbook: Workbook, word: str, log: bool = True) -> Optional[tuple]:
    """ Search a word in the lexicon.

    If the word is found in the lexicon, the function returns in a tuple :
    (the index, the word, its definitions, the timestamp of the addition). If no word was found, returns None.

    Args:
        workbook (Workbook): Workbook object (openpyxl) referring to the spreadsheet.
        word (str): Word to search.
        log (bool): A word that can't be found is considered a warning logging by default, but it's not always useful
        to display the error message when this function is actually used to check whether a word is missing from the
        lexicon.

    Returns:
        tuple: Word found. (index, word, definitions, timestamp).
        None: Word not found.
    """

    word = word.capitalize()

    idx = 2
    found = False
    while idx < first_empty(workbook):
        # Word found
        if workbook[f'A{idx}'].value == word:
            logging.info(f"'{word}' found in lexicon at idx {idx}")
            return idx, word, workbook[f'B{idx}'].value, workbook[f'C{idx}'].value

        # Still searching
        else:
            idx += 1

    # End of itération : word not found
    if not found:
        if log:
            logging.warning(f"'{word}' not found in lexicon")
        return None

def delete(workbook: Workbook, word: str) -> Optional[None]:
    """ Delete a word from the lexicon.

    The delete_rows() function from openpyxl automatically fills the void left by the deletion.

    Args:
        workbook (Workbook): Workbook object (openpyxl) referring to the spreadsheet.
        word (str): Word to delete.

    Returns:
        None: Word not in lexicon.
    """

    word = word.capitalize()

    result = search(workbook, word, log=False) # The function returns None if no word was found.

    # Word not found
    if result is None:
        logging.warning(f"Word '{word}' not deleted : not in lexicon")
        return None

    # Word found
    else:
        idx = result[0]
        workbook.delete_rows(idx)
        logging.info(f"'{word}' deleted from the lexicon")
        excel_file.save("lexi.xlsx")
        logging.debug("xlsx file saved after deletion")
        print(f"The word '{word}' has been deleted from the lexicon.")

def insert(workbook: Workbook, word: str, definition: Union[str, list]) -> Optional[None]:
    """ Manual addition of a word and its definition to the lexicon.

    Args:
        workbook (Workbook): Workbook object (openpyxl) referring to the spreadsheet.
        word (str): Word to insert.
        definition (str or list): Word definition. If there are several definitions, they can be placed in a list.

    Returns:
        None: Word already in lexicon or wrong definition type.
    """

    word = word.capitalize()

    result = search(workbook, word, log=False)  # returns None if no word was found

    # Word already present
    if result is not None:
        idx = result[0]
        logging.warning(f"Word '{word}' already in lexicon at idx {idx}")
        return None

    # Word isn't present
    else:
        row = first_empty(workbook)  # Where to write

        definition_txt = ""

        # 'definition' is a list or a tuple with multiple definitions.
        # Numbering of definitions and merging in a string
        if isinstance(definition, (list, tuple)):
            for idx, d in enumerate(definition):
                definition_txt += f"{idx + 1}) {d} "
                workbook[f'A{row}'] = word
                workbook[f'B{row}'] = definition_txt
                workbook[f'C{row}'] = int(time.time())

        # 'definition' is a string
        elif isinstance(definition, str):
            definition_txt = "1) " + definition
            workbook[f'A{row}'] = word
            workbook[f'B{row}'] = definition_txt
            workbook[f'C{row}'] = int(time.time())

        # Wrong type for 'definition'
        else:
            logging.critical(f"Word '{word}' not inserted : definition must be str or strs in list/tuple")
            return None

        excel_file.save("lexi.xlsx")
        logging.debug("xlsx file saved after insertion")
        print(f"The word '{word}' has been added to the lexicon.")

def add_random_words(dataframe: pd.DataFrame, workbook: Workbook, sample_length: int, seed=None):
    """Adds a given number of random words to the lexicon. Mainly for test purposes.

    Args:
          dataframe (pandas.Dataframe): Dictionary dataframe.
          workbook (Workbook): Workbook object (openpyxl) referring to the spreadsheet.
          sample_length (int): Number of words to add.
          seed (int): Random seed.
    """

    if seed is None:
        sample = dataframe.sample(sample_length)
    else:
        sample = dataframe.sample(sample_length, random_state=seed)

    for idx, word in enumerate(sample["Mot"]):
        add_word(dict_df, workbook, word)

    logging.debug(f"{sample_length} words have been added in the lexicon")
    print(f"{sample_length} words were added to the lexicon.")

    excel_file.save("lexi.xlsx")
    logging.debug("xlsx file saved after adding random sample")

if __name__ == "__main__":
    add_random_words(dict_df, sheet, 10, seed=42) # Insert 10 randomly chosen words in the dictionary

    add_word(dict_df, sheet, "manga") # Add a word from the dictionary
    add_word(dict_df, sheet, "rompicher") # Add a word missing from the dictionary (Logging warning)

    # Manual addition of a word to the lexicon
    insert(sheet, "Valorant", "Jeu de tir à la première personne.")
    insert(sheet, "Luffy", "Personnage principal du manga One Piece.")

    word_to_search = search(sheet, "Luffy") # Find a word in the lexicon
    print(word_to_search)

    delete(sheet, "Valorant") # Deleting a word from the lexicon