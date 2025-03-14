from time import time
import itertools
import logging
from typing import Optional, Union

import pandas as pd

logger = logging.getLogger()

# ===================================================================
#                         DATAFRAME CREATION
# ===================================================================
print("Main dataframe creation...")
df = pd.read_csv("dico.csv")
df = df.sort_values("Mot")
df = df.dropna()
df = df.reset_index(drop=True)
INIT_ROWS = df.shape[0]

# ===================================================================
#                           UTILS FUNCTIONS
# ===================================================================
def percent(partial: Union[int, float], total: Union[int, float], rnd=2):
    """ Calculates the percentage represented by a partial value on a 
    total value.
    
    Args:
        partial: Partial value
        total: Total value
        rnd: Number of decimal places
    """
    
    try:
        return round((partial/total)*100, rnd)
    except ZeroDivisionError:
        return 0

def debug(filter_name: str, start_time: float, end_time: float, rows_before:  int, rows_after: int):
    """This function is called up when each filter in the 
    'multi_filter' function is passed, to gather information 
    on the filter's impact on the initial data (number of rows 
    deleted), as well as on calculation time.
    
    Args:
        filter_name: Current filter name
        start_time: Process start timestamp
        end_time: End of process timestamp
        rows_before: Number of lines before filter application
        rows_after: Number of lines after filter application
    """
    
    exec_time = round(end_time-start_time, 3)
    #rows_del = rows_before - rows_after
    punctual_delta_rows = percent(rows_before - rows_after, rows_before)
    global_delta_rows = percent(INIT_ROWS - rows_after, INIT_ROWS)

    logging.debug(f"""
        --- '{filter_name}' FILTER --- 
        Execution time : {exec_time}s
        Rows before : {rows_before} 
        Rows after : {rows_after}
        Rows deleted : {rows_before - rows_after} 
        Punctual rows variation : (-{punctual_delta_rows}%)
        Global rows variation : (-{global_delta_rows}%)
        """)

# ===================================================================
#                          MULTI FILTERS
# ===================================================================
def multi_filters(dataframe: pd.DataFrame, col_name: str, no_comp: bool=True,
                  length: Optional[int] = None,
                  start_with: Optional[str] = None,
                  end_with: Optional[str] = None,
                  nth_letters: Optional[list[list[int | str]]] = None,
                  contains: Optional[list[str]] = None,
                  not_contain: Optional[list[str]] = None,
                  anagram: Optional[list[str]] = None,
                  log="info"):

    """ Filters a column of words according to a number of filters.

    Args:
        dataframe (pandas.DataFrame): Pandas dataframe containing the column of words to be filtered
        col_name (str): Name of column to filter.
        no_comp (bool): Remove compound words from the analysis.
        length (int): Word length required.
        start_with (str): Letters to appear at the beginning of the word.
        end_with (str): Letters to appear at the end of a word.
        nth_letters (list): Letter to appear in the desired position.
        contains (list): Letters that the word must contain.
        not_contain (list): Letters the word must not contain.
        anagram (list):
        log (str): Enable logging with the desired level (debug, info, warning, critical)
        can be set at None in this case only the CRITICAL will be displayed.
    """
    # Logging initialisation
    if log is not None:
        log = log.upper()
        if log == "DEBUG":
            logger.setLevel(logging.DEBUG)
        elif log == "INFO":
            logger.setLevel(logging.INFO)
        elif log == "WARNING":
            logger.setLevel(logging.WARNING)
        elif log == "CRITICAL":
            logger.setLevel(logging.CRITICAL)
        else:
            logger.setLevel(logging.CRITICAL)
    else:
        logger.setLevel(logging.CRITICAL)

    # -------------------------------------------------------------------
    #                         DATAFRAME CHECK
    # -------------------------------------------------------------------
    if type(dataframe) != pd.DataFrame:
        logging.critical(f"""
        df must be a Pandas dataframe. {type(dataframe)} given """)
        return None
        
    elif col_name not in dataframe.columns:
        logging.critical(f"""
        '{col_name}' column doesn't exist in the dataframe.
        Columns present : {[col for col in dataframe.columns]}""")
        return None
    
    else:
        pass

    # -------------------------------------------------------------------
    #                         CONFLICTS CHECK
    # -------------------------------------------------------------------
    # contains/not_contain check
    if contains is not None and not_contain is not None:
        if not isinstance(contains, list) or not isinstance(not_contain, list):
            logging.critical(f"""'contains' or 'not_contain' isn't a list""")
            return None

        elif set(contains) & set(not_contain):
            logging.critical(f"""
            'contains' and 'not_contain' must not share common values  """)
            return None
        
        else:
            pass

    # -------------------------------------------------------------------
    #                           DEBUG INIT
    # -------------------------------------------------------------------
    INIT_TIME = time()
    INIT_SHAPE = dataframe.shape[0]
    filters_crossed = []

    logging.debug(f"""
    -- INITIAL VALUES --
    Start at : {INIT_TIME}
    Dataframe shape : {dataframe.shape}
    Column to filter : {col_name}
    no_comp = {no_comp}
    length = {length}
    start_with = {start_with}
    end_with = {end_with}
    nth_letters = {nth_letters}
    contains = {contains}
    not_contain = {not_contain}
    anagram = {anagram}
    """)

    print("Filtering...")
    # -------------------------------------------------------------------
    #                             FILTERS
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    #                   FILTER 1 : NO COMPOUND WORDS
    # -------------------------------------------------------------------
    if no_comp:
        start_time = time()

        dataframe = dataframe.loc[
            (~dataframe[col_name].str.contains(r'\s')) &
            (~dataframe[col_name].str.contains(r'-'))
            ]

        end_time = time()
        debug("no_comp", start_time, end_time, INIT_SHAPE, dataframe.shape[0])
        filters_crossed.append("no_comp")

    # -------------------------------------------------------------------
    #                   FILTER 2 : BY WORD LENGTH
    # -------------------------------------------------------------------
    if length is not None:
        if not isinstance(length, int):
            logging.critical(f"""'length' must be of type int. 
            {type(length)} given""")
            return None

        punctual_shape = dataframe.shape[0]
        start_time = time()

        dataframe = dataframe.loc[dataframe[col_name].str.len() == length]

        end_time = time()
        debug("length", start_time, end_time, punctual_shape, dataframe.shape[0])
        filters_crossed.append("length")

    # -------------------------------------------------------------------
    #                 FILTER 3 : BY ABSENCE OF LETTERS
    # -------------------------------------------------------------------
    if not_contain is not None:
        if not isinstance(not_contain, list):
            logging.critical(f"""'not_contain' must be of type list. 
            {type(not_contain)} given""")
            return None

        elif not all(type(x) == str for x in not_contain):
            logging.critical("""One of the elements of 'not_contain' 
            is not a str.""")
            return None
        
        else:
            pass

        not_contain = set(not_contain) # remove duplicates
        r = ""
        for lettre in not_contain:
            r = r + f"(?=.*{lettre})"

        regex = f"^{r}.*$"

        punctual_shape = dataframe.shape[0]
        start_time = time()

        dataframe = dataframe.loc[~dataframe[col_name].str.contains(regex)] # ~ for negation

        end_time = time()
        debug("not_contain", start_time, end_time, punctual_shape, dataframe.shape[0])
        filters_crossed.append("not_contain")

    # -------------------------------------------------------------------
    #                 FILTER 4 : BY PRESENCE OF LETTERS
    # -------------------------------------------------------------------
    if contains is not None:
        if not isinstance(contains, list):
            logging.critical(f"""'contains' must be of type list. 
            {type(contains)} given""")
            return None

        elif not all(type(x) == str for x in contains):
            logging.critical("""One of the elements of 'contains' 
            is not a str.""")
            return None

        contains = set(contains) # remove duplicates
        r = ""
        for lettre in contains:
            r = r + f"(?=.*{lettre})"

        regex = f"^{r}.*$"

        punctual_shape = dataframe.shape[0]
        start_time = time()

        dataframe = dataframe.loc[dataframe[col_name].str.contains(regex)]

        end_time = time()
        debug("contains", start_time, end_time, punctual_shape, dataframe.shape[0])
        filters_crossed.append("contains")

    # -------------------------------------------------------------------
    #                FILTER 5 : BY BEGINNING OF WORD
    # -------------------------------------------------------------------
    if start_with is not None:
        if not isinstance(start_with, str):
            logging.critical(f"""'start_with' must be of type str. 
            {type(start_with)} given""")
            return None

        start_with = start_with.capitalize()

        punctual_shape = dataframe.shape[0]
        start_time = time()

        dataframe = dataframe.loc[dataframe[col_name].str.startswith(start_with)]

        end_time = time()
        debug("start_with", start_time, end_time, punctual_shape, dataframe.shape[0])
        filters_crossed.append("start_with")

    # -------------------------------------------------------------------
    #                   FILTER 6 : BY LETTERS POSITION
    # -------------------------------------------------------------------
    if nth_letters is not None:
        if not isinstance(nth_letters, list):
            logging.critical(f"""'nth_letters' must be of type list. 
            {type(nth_letters)} given""")
            return None
        
        elif not all(type(x)==list and len(x)==2 for x in nth_letters):
            logging.critical(f"""All elements of the 'nth letters' list 
            must be lists of 2 elements: [rank, letter]""")
            return None
        
        elif not all(type(x[0])==int and type(x[1])==str 
        and len(x[1])==1 for x in nth_letters):
            logging.critical(f"""Each sub-element of nth_letters must be a list 
            composed of 2 elements [rank(int), 1 letter (str)]""")
            return None
        
        else:
            pass

        nth_letters = dict(nth_letters)
        
        punctual_shape = dataframe.shape[0]
        start_time = time()

        for rank, letter in nth_letters.items():
            dataframe = dataframe.loc[dataframe[col_name].apply(lambda x: len(x) >
                                                                          int(rank) and x[int(rank) - 1] == letter)]

        end_time = time()
        debug("nth_letters", start_time, end_time, punctual_shape, dataframe.shape[0])
        filters_crossed.append("nth_letters")

    # -------------------------------------------------------------------
    #                    FILTER 7 : BY ENDING OF WORD
    # -------------------------------------------------------------------
    if end_with is not None:
        if not isinstance(start_with, str):
            logging.critical(f"""'start_with' must be of type str. 
            {type(start_with)} given""")
            return None

        punctual_shape = dataframe.shape[0]
        start_time = time()

        dataframe = dataframe.loc[dataframe[col_name].str.endswith(end_with)]

        end_time = time()
        debug("end_with", start_time, end_time, punctual_shape, dataframe.shape[0])
        filters_crossed.append("end_with")

    # -------------------------------------------------------------------
    #                     FILTER 8 : BY ANAGRAM
    # -------------------------------------------------------------------
    if anagram is not None:
        if not isinstance(anagram, list):
            logging.critical(f"""'anagram' must be of type list. 
            {type(anagram)} given""")
            return None

        elif not all(type(x) == str for x in anagram):
            logging.critical("""One of the elements of 'anagram' 
            is not a str.""")
            return None

        start_time = time()
        punctual_shape = dataframe.shape[0]

        # Anagrams generation
        anagrams_dict = {}
        number_of_letters = len(anagram)
        
        """
        Permutations of the letters present in the 'anagram' 
        list so as to form words of different lengths 
        (from length 1 up to a maximum length which is 
        the total number of letters present in the list). 
        Anagrams generated for each word length are added 
        to the 'anagrams_dict' dictionary """
        for i in range(number_of_letters):
            permute = itertools.permutations(anagram, i+1)
            anagrams_of_length_i = set()
            for word in permute:
                word = "".join(word)
                word = word.capitalize()
                anagrams_of_length_i.add(word)
            anagrams_dict[i+1] = anagrams_of_length_i

        # Anagrams grouping
        all_anagrams = [] # all sets
        for anag in anagrams_dict.values():
            all_anagrams.append(anag)
        
        # Merging sets
        merged_sets = all_anagrams[0]
        for set_i in all_anagrams[1:]:
            merged_sets.update(set_i)

        dataframe = dataframe[dataframe[col_name].isin(merged_sets)]

        end_time = time()
        debug("anagram", start_time, end_time, punctual_shape, dataframe.shape[0])
        filters_crossed.append("anagram")
    
    if dataframe.shape[0] == 0:
        logging.info("No words found")
    
    logging.debug(f"""
    -- FINAL STATS -- 
    Total execution time : {round(time() - INIT_TIME, 3)}s
    Filters crossed = {len(filters_crossed)}/8 -> {filters_crossed}
    Total rows deleted : {INIT_SHAPE - dataframe.shape[0]}
    From {INIT_SHAPE} to {dataframe.shape[0]} -> (-{percent(INIT_SHAPE - dataframe.shape[0], INIT_SHAPE, rnd=4)}%)
    """)

    return dataframe

# ===================================================================
#                               MAIN
# ===================================================================
if __name__ == "__main__":
    # Various filters
    dict_filtered = multi_filters(df,
                                  col_name="Mot",
                                  start_with="g",
                                  end_with="it",
                                  contains=["a","u"],
                                  not_contain=["b"],
                                  nth_letters=[[4,"t"]],
                                  length=7)
    print(dict_filtered)

    # By letters position
    letters_position = multi_filters(df,
                                     col_name="Mot",
                                     nth_letters=[[2, "a"], [4,"t"], [6, "r"]])
    print(letters_position)

    # By anagram
    by_anagram = multi_filters(df,
                               col_name="Mot",
                               anagram=["c","a","r","t","e"],
                               length=5)
    print(by_anagram)