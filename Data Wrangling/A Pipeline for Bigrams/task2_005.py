# -*- coding: utf-8 -*-
"""task2_005.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1oXKwg54yrPBOKLJE5g2pWNSIDi7n4f_s

<div class="alert alert-block alert-danger">

# FIT5196 Task 2 in Assessment 1
    
#### Student Name: Emmanuelle Christin; Phakhanan Rataphaibul
#### Student ID: 32941943; 33654735

Date: 16 March 2024


Environment: Python 3.10.12

Libraries used:
* os (for interacting with the operating system, included in Python xxxx)
* pandas 1.1.0 (for dataframe, installed and imported)
* multiprocessing (for performing processes on multi cores, included in Python 3.6.9 package)
* itertools (for performing operations on iterables)
* nltk 3.5 (Natural Language Toolkit, installed and imported)
* nltk.tokenize (for tokenization, installed and imported)
* nltk.stem (for stemming the tokens, installed and imported)

    </div>

<div class="alert alert-block alert-info">
    
## Table of Contents

</div>

[1. Introduction](#Intro) <br>
[2. Importing Libraries](#libs) <br>
[3. Examining Input File](#examine) <br>
[4. Merge All Sheets to Dataframe](#merge) <br>
[5. Text extraction and Data Cleaning](#text) <br>
[6. Generate CSV File](#generate) <br>
[7. Generate the unigram and bigram lists and output as vocab](#step7) <br>
$\;\;\;\;$[7.1. Pre Process to Generate Unigram and Bigram](#step7.1) <br>
$\;\;\;\;$[7.2. Vocabulary List](#step7.2) <br>
[8. Generate Sparse Numerical Representation(Count Vec)](#step8) <br>
$\;\;\;\;$[8.1. Sparse Matrix](#step8.1) <br>
[9. Testing Script](#test) <br>
[10. Summary](#summary) <br>
[11. References](#ref) <br>

<div class="alert alert-block alert-success">
    
## 1.  Introduction  <a class="anchor" name="Intro"></a>

This task involves processing a dataset of YouTube comments from an Excel file and converting them into a numerical representation which will be used in
the model training.

The task aims to generate three output files:

1. `<group_number>_channel_list.csv`: This file contains unique channel IDs along with the counts of top-level comments, considering both all languages and English only.

2. `<group_number>_vocab.txt`: This file consists of unique stemmed tokens sorted alphabetically, presented in the format of `token_index:token`, as specified in Guideline step 4.

3. `<group_number>_countvec.txt`: This file includes numerical representations of all tokens, organized by channel ID and token index, following the format `channel_id, token_index:frequency`.

<div class="alert alert-block alert-success">
    
## 2.  Importing Libraries  <a class="anchor" name="libs"></a>

In this section, we install and import libraries. The following packages were used to accomplish the related tasks:

* **os:** Used for interacting with the operating system, such as navigating through folders, creating directories, or executing commands.

* **re:** Allows for defining and using regular expressions to search, manipulate, and extract patterns from strings.

* **pandas:** Provides data structures and functions for manipulating and analyzing structured data, primarily through DataFrames.

* **multiprocessing:** Enables concurrent execution of Python code across multiple CPU cores, thereby improving performance for CPU-bound tasks.

* **nltk:** The Natural Language Toolkit is a library for natural language processing tasks.

* **sklearn:** Scikit-learn is a machine learning library that provides tools for data mining and data analysis.

* **langdetect:** Used for language detection, which determines the language of a given text.
"""

!pip install langdetect

import os
import re
import pandas as pd
from langdetect import DetectorFactory, detect
import multiprocessing
from itertools import chain
import nltk
from nltk.probability import *
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from nltk.collocations import BigramAssocMeasures, BigramCollocationFinder
from langdetect.lang_detect_exception import LangDetectException
from langdetect import detect_langs
from nltk import ngrams
from nltk.probability import FreqDist

"""-------------------------------------

<div class="alert alert-block alert-success">
    
## 3.  Examining Input File <a class="anchor" name="examine"></a>

First, we connect Google Colab with Google Drive.
"""

from google.colab import drive
drive.mount('/content/drive')

"""Then, we examine the contents of the Excel file. As we can see, there are 30 sheets in the Excel file.


"""

file_path = '/content/drive/Shareddrives/FIT5196_S1_2024/A1/Students data/Task 2/Group005.xlsx'

# Define the file path to the Excel file containing the data
#file_path = '/content/drive/Shareddrives/FIT5196_S1_2024/A1/Sample/Input/sample_input_task2.xlsx'

# Load the Excel file and create an object
xls = pd.ExcelFile(file_path)

# Retrieve all sheets in the file
sheet_names = xls.sheet_names

# Print the number of sheets and their names
print("Number of sheets:", len(sheet_names))
print("Sheet names:", sheet_names)

"""After displaying the first two sheets as a sample of the data, we observed that the cell structures of each sheet vary.

"""

# Define the sheets to display
sheets_to_display = [0, 1]

# Open the Excel file
xls = pd.ExcelFile(file_path)

# Iterate each sheet
for i, sheet_name in enumerate(xls.sheet_names):
    if i in sheets_to_display:
        # Read the current sheet into a DataFrame
        df = pd.read_excel(file_path, sheet_name = sheet_name)

        # Print the sheet name
        print(f"Sheet '{sheet_name}':")

        # Display the first few rows of the DataFrame
        print(df.head())

"""<div class="alert alert-block alert-success">
    
## 4. Merge All Sheets to Dataframe
<a class="anchor" name="merge"></a>

Because each Excel file contains multiple worksheets, where data are positioned differently in each, we combine all data together and remove any duplicates. The logic involves looping through all sheets, merging them into one DataFrame, removing rows with NaN values appearing horizontally and vertically for all rows, and eliminating any duplicate values.
"""

# Dataframe to store the merged data
merged_df = pd.DataFrame()

# Loop through each sheet in the Excel file
for sheet_name in xls.sheet_names:
    # Read the data
    df = pd.read_excel(file_path, sheet_name=sheet_name, dtype={'ID': str, 'Snippet': str})

    # Drop columns that are entirely filled with na values
    df_cleaned = df.dropna(axis=1, how='all')

    # Drop rows that are entirely filled with na values
    df_cleaned = df_cleaned.dropna(axis=0, how='all')

    # Exclude the header
    df_cleaned = df_cleaned.iloc[1:]
    df_cleaned.reset_index(drop=True, inplace=True)

    # Rename the column
    df_cleaned.columns = ['ID', 'Snippet']

    # Concatenate the dataframe
    merged_df = pd.concat([merged_df, df_cleaned], axis=0)

# Remove duplicate rows
merged_df = merged_df.drop_duplicates()

# Print the final shape of the merged dataframe after removing duplicates
print("Final shape of merged DataFrame after removing duplicates:", merged_df.shape)

"""<div class="alert alert-block alert-success">
    
## 5. Text extraction and cleaning
<a class="anchor" name="text"></a>
In this step, we define a function to extract the `textOriginal` fields from all top-level comments using regex to extract the value. Since the comment data contain emojis, we remove them and normalize the text to lowercase for further analysis. We also read the excel in UTF-8 format. The list of emojis to be removed is located in `emoji.txt`.
"""

def extract_text_and_channel(snippet):
    # Regex patterns
    channel_id_match = re.search(r"'channelId': '([^']+)'", snippet)
    text_original_match = re.search(r"'textOriginal': '([^']+)'", snippet)

    # Extracting channelId and textOriginal
    channel_id = channel_id_match.group(1) if channel_id_match else ''
    text_original = text_original_match.group(1) if text_original_match else ''

    return channel_id, text_original

"""After extracting the original text, it will appear like this.

"""

# Extract channelId and textOriginal fields from the Snippet column using the extract_text_and_channel function
merged_df['channelId'], merged_df['textOriginal'] = zip(*merged_df['Snippet'].apply(extract_text_and_channel))

# New DataFrame containing the extracted fields
merged_with_text_original_df = merged_df

# Iterate over the first 10 rows of the DataFrame and print 'channelId' and 'textOriginal' values
for index, row in merged_with_text_original_df.head(10).iterrows():
    channel_id = row['channelId']
    text_original = row['textOriginal']
    print(f"Channel ID: {channel_id}")
    print(f"Text Original: {text_original}")

"""After extracting the `textOriginal` field, we proceed to remove emojis and normalize the text to lowercase within the `textOriginal` column. The list of emojis to remove is stored in `emoji.txt`, which we read using the UTF-8 encoding. We utilize regular expressions to remove emojis."""

file_path = '/content/drive/Shareddrives/FIT5196_S1_2024/A1/emoji.txt'

# Open file list of emoji using utf-8 format
with open(file_path, 'r', encoding = 'utf-8') as file:
  emoji_list = file.read().splitlines()

# Define a regex pattern for matching emojis
emoji_pattern = '|'.join(re.escape(emoji) for emoji in emoji_list)
emoji_pattern = f"[{emoji_pattern}]"

def remove_emojis(text):
    # If the input is a string
    if isinstance(text, str):
        #  Remove the emoji using regex
        removed_emoji_text = re.sub(emoji_pattern, '', text)
        normalised_text = removed_emoji_text.lower()
        # Return value without emoji
        return normalised_text
    else:
        return text

"""Next, we call the function `remove_emojis` and print the first 10 rows of comments without emojis."""

# Apply the remove_emojis function to each text in the textOriginal column
merged_with_text_original_df['textOriginal'] = merged_with_text_original_df['textOriginal'].apply(remove_emojis)

# Iterate over the first 10 rows and print the data
for index, row in merged_with_text_original_df.head(10).iterrows():
    channel_id = row['channelId']
    text_original = row['textOriginal']
    print(f"Channel ID: {channel_id}")
    print(f"Text Original: {text_original}")

"""We prepare a function to detect the language of the `textOriginal` for the next step. We decide the language on a comment level rather than a sentence level using the langdetect library, with `DetectorFactory.seed = 0` set for consistency. Additionally, we create a function to filter out English comments in each row of the dataframe.

"""

DetectorFactory.seed = 0  # Set seed for consistent language detection

def detect_language(comment):
    try:
        return detect_langs(comment)
    except LangDetectException:
        return None

def filter_english_comments(df):
    # Exclude empty comment from filtering english comment
    df = df[df['textOriginal'].str.strip().ne('')]

    # Detect languages for each comment
    df['detected_languages'] = df['textOriginal'].apply(detect_language)
    print("Detected Languages:")
    print(df[['textOriginal', 'detected_languages']])

    # Extract detected languages
    df['detected_languages'] = df['detected_languages'].apply(lambda langs: [lang.lang for lang in langs] if langs else [])

    # Check if English is detected
    df['is_english'] = df['detected_languages'].apply(lambda langs: 'en' in langs)

    # Filter the dataframe to keep only the English comments
    english_df = df[df['is_english']]
    english_df = english_df.drop(columns=['detected_languages', 'is_english'])

    return english_df

"""
<div class="alert alert-block alert-success">
    
## 6. Generate CSV File
<a class="anchor" name="generate"></a>

In this step, we generate a CSV file that includes unique channel IDs along with the counts of top-level comments for all languages as well as English. The CSV file consists of columns named `channel_id`, `all_comment_count`, and `eng_comment_count`. For all comments, we group them by channel ID and calculate the comment count. Similarly, for English comments, we filter them based on language, group them by channel ID, and compute the comment count. Additionally, we filter channel IDs that have at least 15 English comments for subsequent processing."""

# group name
group_number = '005'

# Filter English comments
english_comments_df = filter_english_comments(merged_with_text_original_df)

# Count all comments for each channel
all_comment_counts = merged_with_text_original_df.groupby('channelId').size()

# Count English comments for each channel
eng_comment_counts = english_comments_df.groupby('channelId').size()

# Create dataframe with channel IDs and comment counts
comment_counts_df = pd.DataFrame({
    'channel_id': all_comment_counts.index,
    'all_comment_count': all_comment_counts.values,
    'eng_comment_count': eng_comment_counts.reindex(all_comment_counts.index, fill_value=0).values
})

# Write dataframe to CSV
comment_counts_df.to_csv(f'{group_number}_channel_list.csv', index=False)

# Select channels with at least 15 English comments
selected_channels = eng_comment_counts[eng_comment_counts >= 15]

# Filter dataframe based on selected channels
filtered_df = english_comments_df[english_comments_df['channelId'].isin(selected_channels.index)]

"""<div class="alert alert-block alert-success">
    
## 7. Generate the unigram and bigram lists and output as vocab.txt
<a class="anchor" name="step7"></a>


In this step, we generate both bigrams and unigrams and export them to a file named `vocab.txt`. Here's the breakdown of the process:

A. First, we filter channel IDs that have at least 15 English comments. Then, we perform word tokenization using the regular expression "[a-zA-Z]+".
As we are going to create a vocab, we select only sequences of characters that are part of the English alphabet, excluding any numbers, symbols, punctuation marks, and special characters.

F. Next, we generate the first 200 meaningful bigrams (collocations) using the PMI measure. Additionally, we ensure that these bigrams can be collocated within the same comment.

Justification: We perform this step right after the tokenization and before removing stopwords as bigrams can capture meaningful phrases that provide important contextual clues about the text. Additonally, as our text data are comments gathered from various Youtube channels, hence by generating bigrams before removing stopwords, the idioms or fixed expressions will be preserved as features in the text data. We also ensure these bigrams are within the same comment to maintain context relevance. As we didn't remove these tokens from dataframe, we are able calculate it for countvec.


B part 1. We remove both context-independent and context-dependent stopwords from the vocabulary. For context-independent stopwords, we use the provided `stopwords_en.txt` list.

Justification: After generating bigrams, we remove common stopwords (e.g., "and", "the", etc.) that do not typically add much meaning to the analysis reduces the noise in the data. This helps in focusing on more meaningful words that have potential to contribute significantly to understanding the text's content.


E. Tokens with a length less than 3 are also removed from the vocabulary.

Justification: After removings stopwords, we remove tokens with a length less than three characters as they are less likely to be meaningful (such as prepositions or conjunctions) to make the data cleaner and allow the analysis to be more focused on substantial content.


C. Tokens are stemmed using the Porter stemmer.

Justification: Before removing common tokens and rare token, stemming should be applied as it reduces words to their base or root form. This process helps in reducing the complexity of the dataset and improves the match between different forms of the same word.

B part 2. For context-dependent stopwords, we set a threshold based on words that appear in more than 99% of channel IDs with at least 15 English comments.

Justification: After the stemming process, we can filter out words that appear in more than 99% of channels to eliminate overly common terms specific to the dataset, which might not be informative.

D. Rare tokens are then removed from the vocabulary. We set the threshold to exclude words that appear in less than 1% of channel IDs with at least 15 English comments.

Justification: Removing tokens that appear in less than 1% of channels helps to remove uncommon words that might skew the vocabulary. This threshold ensures that only those words which are relatively common across the vocab are included.

G. Finally, we calculate the vocabulary containing both unigrams and bigrams. We combine them into a single list and sort the list alphabetically in ascending order. The sorted list is then outputted to `vocab.txt`.

<div class="alert alert-block alert-warning">
    
### 7.1. Pre-Process to Generate Unigram and Bigram <a class="anchor" name="step7.1"></a>
"""

# A. Tokenize the text using a regular expression pattern
def tokenize_text(text):
    tokenizer = RegexpTokenizer(r"[a-zA-Z]+")
    tokens = tokenizer.tokenize(text)
    return tokens

# B part 1. Remove stopwords
with open('/content/drive/Shareddrives/FIT5196_S1_2024/A1/stopwords_en.txt', 'r') as file:
    stopwords = set(file.read().splitlines())

def get_stopword_remover(tokens):
    return [token for token in tokens if token not in stopwords]

# C. Stem tokens using Porter Stemmer
porter_stemmer = PorterStemmer()
def stem_tokens(tokens):
    return [porter_stemmer.stem(token) for token in tokens]

# B part 2. Remove common tokens (context-dependent stopwords)
def remove_common_tokens(df, channel_col = 'channelId', common_thresh = 0.99):
    # Get the total number of unique channels
    total_channels = df[channel_col].nunique()
    # Define the threshold number of channels a token must appear in to be considered common
    common_threshold = common_thresh * total_channels
    # Create a dictionary to track in how many different channels each token appears
    token_channel_counts = {token: set() for tokens_list in df['processed_text'] for token in set(tokens_list)}
    # Populate the dictionary with channels for each token
    for index, row in df.iterrows():
        for token in set(row['processed_text']):
            token_channel_counts[token].add(row[channel_col])
    # Determine which tokens meet the common threshold criterion
    common_tokens = {token for token, channels in token_channel_counts.items() if len(channels) > common_threshold}
    # Remove common tokens from the 'processed_text' column
    df['processed_text'] = df['processed_text'].apply(lambda tokens: [token for token in tokens if token not in common_tokens])
    return df

# D. Remove rare tokens
def remove_rare_tokens(df, channel_col = 'channelId', rare_thresh=0.01):
    # Get the total number of unique channels
    total_channels = df[channel_col].nunique()
    # Define the threshold number of channels a token must appear in to be considered rare
    rare_threshold = rare_thresh * total_channels
    # Create a dictionary to track in how many different channels each token appears
    token_channel_counts = {token: set() for tokens_list in df['processed_text'] for token in set(tokens_list)}

    # Populate the dictionary with channels for each token
    for index, row in df.iterrows():
        for token in set(row['processed_text']):
            token_channel_counts[token].add(row[channel_col])
    # Determine which tokens meet the rare threshold criterion
    rare_tokens = {token for token, channels in token_channel_counts.items() if len(channels) < rare_threshold}

    # Remove common tokens from the 'processed_text' column
    df['processed_text'] = df['processed_text'].apply(lambda tokens: [token for token in tokens if token not in rare_tokens])
    return df

# E. Filter tokens with a length less than 3
def filter_tokens(tokens):
    return [token for token in tokens if len(token) >= 3]

# F. Calculate PMI bigrams
def calculate_pmi_bigrams(df, column_name = 'processed_text', top_n = 200):
    # Collect all tokens from all comments
    all_tokens = [token for tokens_list in df[column_name] for token in tokens_list]

    # Initialize BigramCollocationFinder and Bigram Association Measures
    bigram_measures = nltk.collocations.BigramAssocMeasures()
    finder = nltk.collocations.BigramCollocationFinder.from_words(all_tokens)

    # Get the top n bigrams based directly on PMI
    top_bigrams = finder.nbest(bigram_measures.pmi, top_n)

    # Validate bigrams within each comment
    valid_bigrams = []
    for bigram in top_bigrams:
        # Check if bigram occurs consecutively in any comment
        condition_met = df[column_name].apply(
            lambda tokens: bigram[0] in tokens and bigram[1] in tokens and
            (tokens.index(bigram[1]) - tokens.index(bigram[0]) == 1 if bigram[0] in tokens and bigram[1] in tokens else False)
        ).any()
        if condition_met:
            valid_bigrams.append('_'.join(bigram))

 # Merge the valid bigrams in the DataFrame text, replacing them with their underscore-joined version
    for bigram in valid_bigrams:
        bigram_str = '_'.join(bigram)
        df[column_name] = df[column_name].apply(
            lambda tokens: [bigram_str if i < len(tokens) - 1 and tokens[i] == bigram[0] and tokens[i + 1] == bigram[1] else tokens[i] for i in range(len(tokens))]
        )

    return valid_bigrams, df

# G. Calculate the vocabulary
def calculate_vocabulary(df, valid_bigrams_str):
    # To extract only bigram
    all_tokens = [token for tokens_list in df['processed_text'] for token in tokens_list if '_' not in token]

    # Combine sorted unigrams and bigrams into a vocabulary list
    vocabulary_sorted = sorted(set(all_tokens) | set(valid_bigrams_str))

    # Assign indices to vocabulary terms
    vocabulary_with_indices = {term: idx for idx, term in enumerate(vocabulary_sorted)}

    return vocabulary_with_indices

"""This is the result after we tokenize the textOriginal"""

# For resolving the warning
processed_df = filtered_df.copy()
processed_df['processed_text'] = processed_df['textOriginal'].apply(tokenize_text) # A

# Display a sample of processed data
processed_df.head(10)

"""This is the result after we generate bigram"""

bigrams = calculate_pmi_bigrams(processed_df) # F

# Display a sample of the generated bigrams
print(bigrams[0][:10])

"""This is the result after we remove stopword"""

processed_df = bigrams[1].copy()
processed_df['processed_text'] = processed_df['processed_text'].apply(get_stopword_remover) # B part 1

# Display a sample of processed data
processed_df.head(10)

"""This is the result after we remove token less than 3 characters."""

processed_df['processed_text'] = processed_df['processed_text'].apply(filter_tokens) # E

# Display a sample of processed data
processed_df.head(10)

"""This is the result after we stem the token"""

processed_df['processed_text'] = processed_df['processed_text'].apply(stem_tokens) # C

# Display a sample of processed data
processed_df.head(10)

"""This is the result after we remove common token"""

processed_df = remove_common_tokens(processed_df) # B part 2

# Display a sample of processed data
processed_df.head(10)

"""This is the result after we remove rare token"""

processed_df = remove_rare_tokens(processed_df) # D

# Display a sample of processed data
processed_df.head(10)

"""Finally this the result of our vocabulary after merging unigram and bigram"""

vocabulary_with_indices_1 = calculate_vocabulary(processed_df, bigrams[0]) # G

# Display a sample of processed data
print(vocabulary_with_indices_1)

"""After completing all the steps mentioned above, we export the results to `vocab.txt`.

<div class="alert alert-block alert-warning">
    
### 7.2. Vocabulary List <a class="anchor" name="step7.2"></a>

Now we want to write the vocab to txt
"""

# Define a function to output the vocabulary to a file
def output_vocab_to_file(vocabulary_with_indices, output_file = f'{group_number}_vocab.txt'):
    with open(output_file, "w", encoding = 'utf-8') as file:
        # Iterate over the vocabulary terms and their indices
        for term, idx in vocabulary_with_indices.items():
            # Write each term and its index to the file
            file.write(f"{term}:{idx}\n")

# Call the function to output the vocabulary
output_vocab_to_file(vocabulary_with_indices_1)

"""<div class="alert alert-block alert-success">
    
## 8. Generate the sparse numerical representation and output as countvec.txt. <a class="anchor" name="step8"></a>

In this step, we count the frequency of unigrams and bigrams that were generated before using FreqDist(). Additionally, we map the generated tokens with the vocabulary obtained in step 7 (stored in vocabulary_with_indices). Then, we write the sparse numerical representation based on each channel ID to a text file.
"""

# Function to process each channel ID
def process_group(group):
    # All Token in column 'processed_text' (Modified column we get from step 4)
    all_tokens = [token for tokens_list in group['processed_text'] for token in tokens_list]
    # Calculate frequency distribution of tokens
    fd = FreqDist(all_tokens)
    # Replace tokens with indices and filter out tokens not present in the vocabulary
    fd_indexed = FreqDist({vocabulary_with_indices_1.get(token, 0): count for token, count in fd.items() if token in vocabulary_with_indices_1})
    return fd_indexed

# Group by 'channel_id' and apply calculate freq func
groupped_fd = processed_df.groupby('channelId').apply(process_group)

"""<div class="alert alert-block alert-warning">
    
### 8.1. Sparse Matrix <a class="anchor" name="step8.1"></a>

In this step, we write the frequency of the token of each channel to a text file `countvec.txt`
"""

# Function to write the frequency distribution of tokens for each channel to a text file
def write_channel_frequencies_to_file(grouped_fd, file_path = f'{group_number}_countvec.txt'):
    # Open File
    with open(file_path, 'w') as file:
        # Iterate over each channel and its frequency distribution
        for channel_id, fd in grouped_fd.items():
            # Generate the formatted for each token-index and its count
            token_counts = ','.join([f"{token}:{count}" for token, count in fd.most_common()])
            # Write to the file
            file.write(f"{channel_id},{token_counts}\n")

    print(f"Data has been written to '{file_path}'")

# Call the function
write_channel_frequencies_to_file(groupped_fd)

"""-------------------------------------

<div class="alert alert-block alert-success">
    
## 9. Testing Script <a class="anchor" name="test"></a>
"""

import pandas as pd
import itertools

groupnum = input("Please input your group number:")
df = pd.read_csv("{}_channel_list.csv".format(groupnum.zfill(3)))
df_col = ["channel_id", "all_comment_count", "eng_comment_count"]
assert all(df.columns == df_col) == True, "check your csv columns!"

print("Task 2 csv file passed!")

with open("{}_vocab.txt".format(groupnum.zfill(3)), "r") as file:
    vocab = file.readlines()
try:
    vocab = [each.strip().split(":") for each in vocab]
except:
    raise ValueError("Vocab file structured incorrectly!")

print("Task 2 vocab file passed!")

with open("{}_countvec.txt".format(groupnum.zfill(3)), "r") as file:
    countvec = file.readlines()

countvec = [each.strip().split(",") for each in countvec]
assert (
    all([":" not in each[0] for each in countvec]) == True
), "The channel id in countvec doesn't look right!"
try:
    allcounts = list(itertools.chain.from_iterable([each[1:] for each in countvec]))
    ind_counts = [each.split(":") for each in allcounts]
    # testing whether the ind:count can be parsed as numerical values
    [(int(each[0]), int(each[1])) for each in ind_counts]
except:
    raise ValueError("The ind:count part of your countvec doesnt look right!")

print("Task 2 countvec file passed!")

"""-------------------------------------

<div class="alert alert-block alert-success">
    
## 10. Summary <a class="anchor" name="summary"></a>

In this task, we utilized Python to extract specific data from an Excel file:

- **Extracting Text Using Regex:** Initially, we consolidated all sheets in the Excel file into a single dataframe. From there, we extracted the channel ID and textOriginal from the snippet column.

- **Preprocessing:** We conducted preprocessing steps such as removing emojis.

- **Language Filtering:** Utilizing the langdetect package, we filtered comments by language, counting based on channel ID, all language comments, and English comments, storing the results in the channel_list.

- **Generating Bigrams and Unigrams:** Employing the nltk and re packages, we generated both unigrams and bigrams based on the channel list, specifically focusing on those with at least 15 English comments. The resulting data was stored in vocab.txt.

- **Sparse Vectorization:** Using the FreqDist function, we calculated the frequency of all bigrams and unigrams in the text original column that was extracted previously. Subsequently, we formatted the results accordingly and saved them to countvec.txt.

-------------------------------------

<div class="alert alert-block alert-success">
    
## 11. References <a class="anchor" name="ref"></a>

[1] Bigram and Collocation, https://www.nltk.org/howto/collocations.html.

[2] Combining dataframe in panda, https://realpython.com/pandas-merge-join-and-concat/

[3] FreqDist, https://www.nltk.org/api/nltk.probability.FreqDist.html.

[4] Regex Sub, https://www.geeksforgeeks.org/python-substituting-patterns-in-text-using-regex/

[5] Working with Excel, https://www.geeksforgeeks.org/working-with-excel-files-using-pandas/

## --------------------------------------------------------------------------------------------------------------------------
"""